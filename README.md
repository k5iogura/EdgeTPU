# Estimation of Google Edge TPU Accelerator

Estimates Edge TPU performace on some linux system such as RaspberryPi, [Rock64@Pine64](https://www.pine64.org/?product=rock64-media-board-computer) etc.  

As of now, Raspbian OS bases on Ubuntu Xenial(16.04 LTS) build as 32bit OS.  

Rock64@Pine64 has compatible form factor of RaspberryPi 3 Model B(+), but Rock64@Pine64 supports many variant Destribution of Linux such as Ambian, Ubuntu, Debian etc. android too, and supports 32bit and 64bit OS.    

RaspberryPi-3 has 4 USB-2.0 ports.  
Rock64@Pine64 has 2 USB-2.0 ports and 1 USB-3.0 port.  
Edge TPU expects using USB-3.0 and 64bit aarch64 OS, therefore Rock64@Pine64 is suitable for Edge TPU.  

## Getting start of Google Edge TPU Accelerator Coral.  
[Getting start](https://coral.withgoogle.com/docs/accelerator/get-started/)  

Requirements  
Any Linux computer with a USB port  
  Debian 6.0 or higher, or any derivative thereof (such as Ubuntu 10.0+)  
  System architecture of either x86_64 or ARM64 with ARMv8 instruction set  
And yes, this means Raspberry Pi is supported. However, it must be Raspberry Pi 2/3 Model B/B+ running Raspbian (or another Debian derivative).  

It's a very easy to install Edge TPU on linux system but not be supported Windows OS.  
Needs Internet access from host system.  

```
cd ~/
wget https://dl.google.com/coral/edgetpu_api/edgetpu_api_latest.tar.gz -O edgetpu_api.tar.gz --trust-server-names
tar xzf edgetpu_api.tar.gz
cd edgetpu_api
bash ./install.sh
```

Investigating *install.sh* script we can found out that script supports bellow CPU architectures,  

- armv7l  
  When uname -m returns *armv7l*, 32bit library is installed on somewhere of /usr/lib...  

- x86_64 or aarch64  
  When uname -m returns *x86_64* or *aarch64* 64bit library is installed on somewhere of /usr/lib...  
  If system was 32bit OS on 64bit Hardware 64bit library will be installed and may be system fall into crash!  

## Edge TPU Accelerator on Rock64@Pine64  

- [Software download](http://wiki.pine64.org/index.php/ROCK64_Software_Release)  
There are latest version OS supported by Rock64.  

- [Software github](https://github.com/ayufan-rock64/linux-build/releases)  
There are archives of OS images.  

## Edge TPU Accelerator on RaspberryPi-3 Model B+  
