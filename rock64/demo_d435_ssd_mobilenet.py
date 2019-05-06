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
    def __init__(self, color=True, depth=False):
        self.color    = color
        self.depth    = depth
        self.pipeline = rs.pipeline()
        config        = rs.config()
        self.align_to = rs.stream.color
        self.align    = rs.align(self.align_to)
        if color: config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        if depth: config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16,  30)
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
  parser.add_argument( '-crw', '--camera_w', type=int, default=320, help='camera resolution')
  parser.add_argument( '-crh', '--camera_h', type=int, default=240, help='camera resolution')
  parser.add_argument( '-rww', '--resize_w', type=int, default=592, help='resize view windows')
  parser.add_argument( '-rwh', '--resize_h', type=int, default=432, help='resize view windows')
  args = parser.parse_args()

  # Initialize engine.
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None

  # Open image.
  #img = Image.open(args.input)
  #draw = ImageDraw.Draw(img)
  #cam = cv2.VideoCapture(0)
  #assert cam is not None
  cam = D435()
  print("Opened UVC-Camera via /dev/video0")
  #cam.set(cv2.CAP_PROP_FPS,30)
  #cam.set(cv2.CAP_PROP_FRAME_WIDTH,args.camera_w)
  #cam.set(cv2.CAP_PROP_FRAME_HEIGHT,args.camera_h)

  start = time()
  img_count=0
  while True:
      #r, Img = cam.read()
      #assert r is True
      #img = cv2.cvtColor(Img, cv2.COLOR_BGR2RGB)
      #img = Image.fromarray(np.uint8(img))
      Img, dpth = cam.read()
      img = cv2.resize(Img,(320,240))
      #print(img.shape, img[:10])
      #break
      img = Image.fromarray(np.uint8(img))
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
          Img = cv2.rectangle(Img,(box[0],box[1]),(box[2],box[3]),(255,255,255),2)
        Img = cv2.resize(Img,(args.resize_w, args.resize_h))
      cv2.imshow('demo',Img)
      key=cv2.waitKey(1)
      if key==27: break
      continue
  cam.close()

if __name__ == '__main__':
  main()
