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

r"""A demo for object detection.

For Raspberry Pi, you need to install 'feh' as image viewer:
sudo apt-get install feh

Example (Running under python-tflite-source/edgetpu directory):

  - Under the parent directory python-tflite-source.

  - Face detection:
    python3.5 edgetpu/demo/object_detection.py \
    --model='test_data/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite' \
    --input='test_data/face.jpg'

  - Pet detection:
    python3.5 edgetpu/demo/object_detection.py \
    --model='test_data/ssd_mobilenet_v1_fine_tuned_edgetpu.tflite' \
    --label='test_data/pet_labels.txt' \
    --input='test_data/pets.jpg'

'--output' is an optional flag to specify file name of output image.
"""

import argparse
import platform
import subprocess
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from PIL import ImageDraw
from pdb import *
import sys, os
import cv2
import numpy as np
from time import time

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

  if not args.output:
    output_name = 'object_detection_result.jpg'
  else:
    output_name = args.output

  # Initialize engine.
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None

  # Open image.
  #img = Image.open(args.input)
  #draw = ImageDraw.Draw(img)
  cam = cv2.VideoCapture(0)
  assert cam is not None
  print("Opened UVC-Camera via /dev/video0")
  cam.set(cv2.CAP_PROP_FPS,30)
  cam.set(cv2.CAP_PROP_FRAME_WIDTH,args.camera_w)
  cam.set(cv2.CAP_PROP_FRAME_HEIGHT,args.camera_h)

  start = time()
  img_count=0
  while True:
      r, Img = cam.read()
      assert r is True
      img = cv2.cvtColor(Img, cv2.COLOR_BGR2RGB)
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

if __name__ == '__main__':
  main()
