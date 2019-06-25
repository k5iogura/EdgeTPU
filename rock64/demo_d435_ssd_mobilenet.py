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
from time import time

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
        self.pipeline.start(config)

    def read(self):
        color_frame = depth_frame = None
        frame = self.pipeline.wait_for_frames()
        align_frame = self.align.process(frame)
        if self.color:
            color_frame = align_frame.get_color_frame()
            color_frame = np.asanyarray(color_frame.get_data())
        if self.depth:
            depth_frame = align_frame.get_depth_frame()
        return color_frame, depth_frame

    def close(self):
        self.pipeline.stop()

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
  parser.add_argument( '-d', '--depth',      action='store_true')
  parser.add_argument( '-uvc', '--uvc',      action='store_true')
  parser.add_argument( '-crw', '--NN_w',     type=int, default=320, help='NeuralNet in-width size')
  parser.add_argument( '-crh', '--NN_h',     type=int, default=240, help='NeuralNet in-height size')
  parser.add_argument( '-rww', '--resize_w', type=int, default=592, help='resize view windows width')
  parser.add_argument( '-rwh', '--resize_h', type=int, default=432, help='resize view windows height')
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
  img_count=0
  ratio_w = args.resize_w/args.NN_w
  ratio_h = args.resize_h/args.NN_h
  while True:
      if start is None: start = time()
      if args.uvc:
          r, Img_org = cam.read()
          assert r is True
          Img = cv2.cvtColor(Img_org, cv2.COLOR_BGR2RGB)
      else:
          Img_org, dpth = cam.read()
          Img = cv2.resize(Img_org,(args.NN_w,args.NN_h))
      img = Image.fromarray(np.uint8(Img))
      draw = ImageDraw.Draw(img)

      # Run inference.
      ans = engine.DetectWithImage(img, threshold=args.threshold, keep_aspect_ratio=True,
                                   relative_coord=False, top_k=10)
      during = (time()-start)
      img_count+=1
      sys.stdout.write('\b'*20)
      sys.stdout.write("%.3fFPS"%(img_count/during))
      sys.stdout.flush()
      if ans:
        for obj in ans:
          box = obj.bounding_box.flatten()
          box = np.asarray(box,dtype=np.int)
          rect_lt = (int( ratio_w * box[0] ), int( ratio_h * box[1] ))
          rect_rb = (int( ratio_w * box[2] ), int( ratio_h * box[3] ))
          Img = cv2.rectangle(Img_org, rect_lt, rect_rb, (255,255,255), 2)
      cv2.imshow('demo',Img_org)
      key=cv2.waitKey(1)
      if key==27: break
      continue

  print("\nfin")
  cv2.destroyAllWindows()
  if args.uvc:
      cam.release()
  else:
      cam.close()

if __name__ == '__main__':
  main()
