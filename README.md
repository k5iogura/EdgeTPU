# Estimation of Google Edge TPU Accelerator

Estimates Edge TPU performace on some linux system such as RaspberryPi, [Rock64@Pine64](https://www.pine64.org/?product=rock64-media-board-computer) etc.  

As of now, Raspbian OS bases on Ubuntu Xenial(16.04 LTS) build as 32bit OS.  

Rock64@Pine64 has compatible form factor of RaspberryPi 3 Model B(+), but Rock64@Pine64 supports many variant Destribution of Linux such as Ambian, Ubuntu, Debian etc. android too, and supports 32bit and 64bit OS.    

## Getting start of Google Edge TPU Accelerator Coral.  
[Getting start](https://coral.withgoogle.com/docs/accelerator/get-started/)  

It's a very easy to install Edge TPU on linux system but not be supported Windows OS.  

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

- x86_64  
- aarch64  
  When uname -m returns *x86_64* or *aarch64* 64bit library is installed on somewhere of /usr/lib...  
  If system was 32bit OS on 64bit Hardware 64bit library will be installed and may be system fall into crash!  

## Edge TPU Accelerator on Rock64@Pine64  

- [Software download](http://wiki.pine64.org/index.php/ROCK64_Software_Release)  
There are latest version OS supported by Rock64.  

- [Software github](https://github.com/ayufan-rock64/linux-build/releases)  
There are archives of OS images.  

## Edge TPU Accelerator on RaspberryPi-3 Model B+  
