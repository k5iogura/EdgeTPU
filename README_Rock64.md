# Neural Network DEMO with Rock64@Pine64 compatible RaspberryPi with USB3.0

![](files/OpeningArmbian.png)  

## Installation of Requirement packages

### OpenCV with Python3.5  
Needs installation from source code.  

- First of all,  
apt install bellow,  
python3-pip python-pip  
pip3 install setuptools  

To avoid pip SSL certificate error, edit ~/.pip/pip.conf like bellow,
[global]
trusted-host = pypi.python.org
               pypi.org
               files.pythonhosted.org

- apt install for requirements  
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
    $ make j4  
```
