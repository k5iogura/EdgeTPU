# Neural Network DEMO with Rock64@Pine64 compatible RaspberryPi with USB3.0

![](files/OpeningArmbian.png)  

## Installation of Requirement packages

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
[global]  
trusted-host = pypi.python.org  
               pypi.org  
               files.pythonhosted.org  

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

