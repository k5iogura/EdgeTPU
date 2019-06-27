#! /usr/bin/env python3
import argparse
import platform
import subprocess
from edgetpu.detection.engine import DetectionEngine
import pyrealsense2 as rs
from PIL import Image
from PIL import ImageDraw
from pdb import *
import sys, os
import cv2
import numpy as np
from time import time, sleep
from pdb import *

class D435:
    def __init__(self, color=True, depth=False, w=640, h=480, fps=30):
        self.color    = color
        self.depth    = depth
        self.pipeline = rs.pipeline()
        config        = rs.config()
        self.align_to = rs.stream.color
        self.align    = rs.align(self.align_to)
        if color: config.enable_stream(rs.stream.color, w, h, rs.format.bgr8, fps)
        if depth: config.enable_stream(rs.stream.depth, w, h, rs.format.z16,  fps)
        profile = self.pipeline.start(config)
        self.scale    = profile.get_device().first_depth_sensor().get_depth_scale()
        print("depth_sensor_scale:",self.scale)

    def read(self):
        color_frame = depth_frame = None
        frame = self.pipeline.wait_for_frames()
        align_frame = self.align.process(frame)
        if self.color:
            color_frame = align_frame.get_color_frame()
            color_frame = np.asanyarray(color_frame.get_data())
        if self.depth:
            depth_frame = align_frame.get_depth_frame()
            depth_frame1= depth_frame.as_depth_frame()
            depth_array = np.asanyarray(depth_frame.get_data())
        return color_frame, depth_frame, depth_array

    def release(self):
        sleep(1)
        self.pipeline.stop()
        sleep(1)

# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r', encoding="utf-8") as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-m', '--model', type=str,
      default='../model/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite',
      help='Path of the detection model.'
  )
  parser.add_argument(
      '-l', '--label',type=str,
      default='../model/coco_labels.txt',
      help='Path of the labels file.'
  )
  parser.add_argument(
      '--input', help='File path of the input image.')
  parser.add_argument(
      '--output', help='File path of the output image.')
  parser.add_argument(
      '--threshold', type=float, default=0.45, help='Threshold for DetectionEngine')
  parser.add_argument( '-d',   '--depth',    action='store_true')
  parser.add_argument( '-r',   '--rect',     action='store_true')
  parser.add_argument( '-uvc', '--uvc',      action='store_true')
  parser.add_argument( '-center', '--object_center', action='store_true')
  parser.add_argument( '-crw', '--NN_w',     type=int, default=320, help='NeuralNet in-width size')
  parser.add_argument( '-crh', '--NN_h',     type=int, default=240, help='NeuralNet in-height size')
  parser.add_argument( '-rww', '--resize_w', type=int, default=640, help='resize view windows width')
  parser.add_argument( '-rwh', '--resize_h', type=int, default=480, help='resize view windows height')
  args = parser.parse_args()

  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None

  print("NN: {} {} | uvc: {} | depth : {}".format(args.NN_w, args.NN_h, args.uvc, args.depth))
  if args.uvc:
      cam = cv2.VideoCapture(0)
      assert cam is not None
      print("Opened UVC-Camera via /dev/video0")
      cam.set(cv2.CAP_PROP_FPS,30)
      cam.set(cv2.CAP_PROP_FRAME_WIDTH,args.NN_w)
      cam.set(cv2.CAP_PROP_FRAME_HEIGHT,args.NN_h)
  else:
      cam = D435(color=True, depth=args.depth)

  start = None
  img_count = 0
  seg = None
  ratio_w = args.resize_w/args.NN_w
  ratio_h = args.resize_h/args.NN_h
  while True:
      if start is None: start = time()
      cam_start = time()
      if args.uvc:
          r, Img_org = cam.read()
          assert r is True
          Img = cv2.cvtColor(Img_org, cv2.COLOR_BGR2RGB)
      else:
          Img_org, dth, dth_np = cam.read()
          Img = cv2.resize(Img_org,(args.NN_w,args.NN_h))
      if seg is None: seg = np.zeros(Img_org.shape,dtype=np.uint8)
      img = Image.fromarray(np.uint8(Img))
      #draw = ImageDraw.Draw(img)

      # Run inference.
      cam_time = time() - cam_start
      inf_start = time()
      ans = engine.DetectWithImage(img, threshold=args.threshold, keep_aspect_ratio=True,
                                   relative_coord=False, top_k=10)
      inf_time = time() - inf_start
      drw_start= time()
      img_count+=1
      if ans:
        seg = (seg/2).astype(np.uint8)
        for obj in ans:
            txt = labels[obj.label_id]
            box = obj.bounding_box.flatten()                                # coord NN-in
            box = np.asarray(box,dtype=np.int)
            rect_lt = (int( ratio_w * box[0] ), int( ratio_h * box[1] ))    # coord Camera-out
            rect_rb = (int( ratio_w * box[2] ), int( ratio_h * box[3] ))
            rect_xy = (int(rect_lt[0]+(rect_rb[0] - rect_lt[0])/2),int(rect_lt[1]+(rect_rb[1] - rect_lt[1])/2))
            if args.depth:
                if not args.object_center:
                    dth_obj_m= dth_np[rect_lt[1]:rect_rb[1], rect_lt[0]:rect_rb[0]]*cam.scale
                    dth_obj_m = np.clip(dth_obj_m, 0.001, 10.000)         # histogram of meter wise until 20m
                    bins, range_m = np.histogram(dth_obj_m, bins=10)
                    index_floor = np.argmax(bins)                         # range which occupy most area in bbox
                    range_floor = range_m[index_floor]
                    range_ceil  = range_m[index_floor+1]
                    indexXY = np.where((dth_obj_m>range_floor) & (dth_obj_m<range_ceil))
                    if len(indexXY[0]) == 0 and len(indexXY[1]) == 0:continue
                    meters  = dth_obj_m[indexXY].min()
                    indexXY = (indexXY[0]+rect_lt[1], indexXY[1]+rect_lt[0])
#                    Img_org[indexXY[0], indexXY[1], 2] = 128
                    seg[indexXY[0], indexXY[1], 2] = 255
                else:
                    meters = dth.get_distance(rect_xy[1], rect_xy[0])  # show center of bbox
                txt    = txt + " %.2fm"%(meters)
            if args.rect: cv2.rectangle(Img_org, rect_lt, rect_rb, (255,255,255), 2)
            cv2.putText(Img_org, txt, rect_xy, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
      Img_org = Img_org | seg
      cv2.imshow('demo',Img_org)
      key=cv2.waitKey(1)
      if key==27: break
      during = (time()-start)
      drw_time = time() - drw_start
      sys.stdout.write('\b'*80)
      sys.stdout.write(
          "%.3fFPS cam:%.3f inf:%.3f drw:%.3f %dobjects"%
          (img_count/during, cam_time, inf_time, drw_time, len(ans))
      )
      sys.stdout.flush()
      continue

  print("\nfin")
  cv2.destroyAllWindows()
  cam.release()

if __name__ == '__main__':
  main()
