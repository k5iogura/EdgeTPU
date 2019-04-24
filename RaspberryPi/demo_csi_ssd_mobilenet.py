# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Supports Pi-Camera CSI Inteface via picamera package.
# Unsupports USB-Camera.
# Tested Mobilenet_ssd_v2 model trained with coco dataset.

import argparse
from PIL import Image
from PIL import ImageDraw
from pdb import *
import sys, os
import cv2
import numpy as np
from time import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from edgetpu.detection.engine import DetectionEngine

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
  def check_file(path):
        if os.path.exists(path) is True: return path
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-m', '--model', type=check_file,
      default='../model/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite',
      help='Path of the detection model.'
  )
  parser.add_argument(
      '-l', '--label',type=check_file,
      default='../model/coco_labels.txt',
      help='Path of the labels file.'
  )
  parser.add_argument("-th",  "--threshold",          type=float, default=0.45, help='Threshold for DetectionEngine')
  parser.add_argument("-cfr", "--camera_framerate",   type=int,   default= 120,help="Maximum Framerate for CSI")
  parser.add_argument("-crw", "--camera_resolution_w",type=int,   default= 320,help="Camera Width")
  parser.add_argument("-crh", "--camera_resolution_h",type=int,   default= 240,help="Camera Height")
  args = parser.parse_args()

  # Initialize engine.
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label)

  camera = PiCamera()
  camera.framerate = args.camera_framerate
  camera.resolution = (args.camera_resolution_w, args.camera_resolution_h)
  rawCapture = PiRGBArray(camera, size=(args.camera_resolution_w, args.camera_resolution_h))

  start = time()
  img_done = 0
  for csi_cam in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
      Img = csi_cam.array
      rawCapture.truncate(0)
      img = Image.fromarray(np.uint8(Img))
      draw = ImageDraw.Draw(img)

      # Run inference.
      ans = engine.DetectWithImage(img, threshold=args.threshold, keep_aspect_ratio=True,
                                   relative_coord=False, top_k=10)
      elapsed = (time()-start)
      if img_done==0: print("CameraIn = ",Img.shape)
      img_done+=1
      sys.stdout.write('\b'*20)
      sys.stdout.write("%.2fFPS"%(img_done/elapsed))
      sys.stdout.flush()

      if ans:
        Img = cv2.cvtColor(Img,cv2.COLOR_RGB2BGR)
        for obj in ans:
          box = obj.bounding_box.flatten()
          box = np.asarray(box,dtype=np.int)
          Img = cv2.rectangle(Img,(box[0],box[1]),(box[2],box[3]),(255,255,255),2)
      cv2.imshow('MobileNet-SSD',Img)
      key=cv2.waitKey(1)
      if key==27: break
  print("\nfinalize")
  cv2.destroyAllWindows()

if __name__ == '__main__':
  main()
