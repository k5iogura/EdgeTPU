# Neural Network DEMO with Rock64@Pine64 aarch64 OS and USB3.0

![](files/OpeningArmbian.png)  

## Installation of Packages for Demo

### OpenCV with Python3.5  
Needs installation from source code reason why pip3 not providing comaptible opencv-phton.  

- First of all,  
Install bellow in SDCard(>16GB) by Ethcer,  
Armbian_5.75_Rock64_Debian_stretch_default_4.4.174_desktop.img  
boot!

- apt install bellow,  
python3-pip python-pip  
pip3 install setuptools  

- Check Python --version  
3.5.3

- To avoid pip SSL certificate error, edit ~/.pip/pip.conf like bellow,  
```
[global]  
trusted-host = pypi.python.org  
               pypi.org  
               files.pythonhosted.org  
```

- apt install for requirements of opencv 3.4.3  
build-essential cmake unzip pkg-config  
libjpeg-dev libpng-dev libtiff-dev  
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev  
libxvidcore-dev libx264-dev  
libgtk-3-dev  
libatlas-base-dev gfortran  
python3-dev  

- Build from source  
```
    $ wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.3.zip --no-check-certificate  
    $ wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/3.4.3.zip --no-check-certificate  
    
    $ unzip opencv.zip  
    $ unzip opencv_contrib.zip  
    
    $ pip3 install numpy  
    
    $ cd opencv-3.4.3  
    $ mkdir build;cd build  
    cmake -D CMAKE_BUILD_TYPE=RELEASE \  
    -D CMAKE_INSTALL_PREFIX=/usr/local \  
    -D INSTALL_PYTHON_EXAMPLES=ON \  
    -D INSTALL_C_EXAMPLES=OFF \  
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.3/modules \  
    -D PYTHON_EXECUTABLE=/usr/bin/python3 \  
    -D BUILD_EXAMPLES=OFF ..  
    $ make -j4  
    # make install
    # ldconfig
```
Over 4 hours has elapsed to compile source, Hwuuh,  

- Check build process like bellow,  
```
    $ pkg-config --modversion opencv
      3.4.3
    $ find . -iname cv2\*.so
      ./lib/python3/cv2.cpython-35m-aarch64-linux-gnu.so
    $ python3 
      Python 3.5.3 (default, Sep 27 2018, 17:25:39) 
      [GCC 6.3.0 20170516] on linux
      Type "help", "copyright", "credits" or "license" for more information.
      >>> import cv2
      >>> cv2.__version__
      '3.4.3'
      >>> 
```
  Completed opencv installation for Python3  

- Check UVC Camera  
  Create cam.py script like bellow,  

  ```
  import numpy as np
  import cv2
  import sys,os
  cam = cv2.VideoCapture(0)
  assert cam is not None
  while True:
    r,f = cam.read()
    assert r is True

    cv2.imshow('camera',f)
    if cv2.waitKey(33)!=-1:break

  print("finalize")
  cam.release()
  ```

  ```
  $ python3 cam.py
  ```

  *Very Fast and Short latency* inspite of USB Camera.  

### Install edgetpu_api and simple Demos  

- Install edgetpu_api.  

 ```
    $ cd ~/
    $ wget https://dl.google.com/coral/edgetpu_api/edgetpu_api_latest.tar.gz \
      -O edgetpu_api.tar.gz --trust-server-names --no-check-certificate
    $ tar xzf edgetpu_api.tar.gz
    $ cd edgetpu_api
    $ bash ./install.sh
 ```
 
- Run *ClassificationEngine* demo  

 ```
 $ cd ~/Downloads/
 $ wget https://storage.googleapis.com/cloud-iot-edge-pretrained-models/canned_models/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
    http://storage.googleapis.com/cloud-iot-edge-pretrained-models/canned_models/inat_bird_labels.txt \
    https://coral.withgoogle.com/static/images/parrot.jpg  --no-check-certificate
 $ cd /usr/local/lib/python3.5/dist-packages/edgetpu/demo
 $ python3 classify_image.py --model ~/Downloads/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--label ~/Downloads/inat_bird_labels.txt --image ~/Downloads/parrot.jpg
W0721 22:20:01.232883    3945 package_registry.cc:65] Minimum runtime version required by package (5)
is lower than expected (10).
 ---------------------------
 Ara macao (Scarlet Macaw)
 Score :  0.761719
 ```
Work fine.  

## Object Detection a image-file Demo with ssd_mobilenet

- Demo script  
  Use object_detection.py **in this repo**.  
  Looking at sample script object_detection.py EdgeTPU is in not only prediction but also a part of postprocess. Therefore only overlaying bounding boxes on image is user task.  

- Test image  
```
$ wget --no-check-certificate https://coral.withgoogle.com/static/images/face.jpg
```
- MobileNet SSD v1 (COCO) model and label  
Detects the location of 90 types objects  
Dataset: COCO  
Input size: 300x300  

```
$ mkdir ~/ssd_mobilenet_v1; cd ~/ssd_mobilenet_v1

$ wget --no-check-certificate http://storage.googleapis.com/cloud-iot-edge-pretrained-models/canned_models/mobilenet_ssd_v1_coco_quant_postprocess_edgetpu.tflite
$ wget --no-check-certificate http://storage.googleapis.com/cloud-iot-edge-pretrained-models/canned_models/coco_labels.txt

$ python3 object_detection.py \
  --model mobilenet_ssd_v1_coco_quant_postprocess_edgetpu.tflite \
  --label coco_labels.txt \
  --input face.jpg \
  --output person_result.jpg
```

- MobileNet SSD v2 (COCO) model and label  

```
$ mkdir ~/ssd_mobilenet_v2; cd ~/ssd_mobilenet_v2

$ wget --no-check-certificate http://storage.googleapis.com/cloud-iot-edge-pretrained-models/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
$ wget --no-check-certificate http://storage.googleapis.com/cloud-iot-edge-pretrained-models/canned_models/coco_labels.txt

$ python3 object_detection.py \
  --model mobilenet_ssd_v1_coco_quant_postprocess_edgetpu.tflite \
  --label coco_labels.txt \
  --input face.jpg \
  --output person_result.jpg
```
*person_result.jpg* via MobileNet SSD v2.  
![](rock64/person_result.jpg)  

## Object Detection via UVC Camera with ssd_mobilenet  
Connect UVC Camera via USB 2.0 port and Edge TPU Accelerator via USB 3.0.  
```
  $ cd rock64
  $ python3 demo_uvc_ssd_mobilenet.py  
```
