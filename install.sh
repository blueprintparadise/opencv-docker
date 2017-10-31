#!/bin/bash
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install build-essential
sudo apt-get -y install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get -y install libgtk-3-dev
sudo apt-get -y install libxvidcore-dev libx264-dev
sudo apt-get -y install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
sudo apt-get -y install libjpeg8-dev libtiff5-dev libpng12-dev
sudo apt-get -y install libatlas-base-dev gfortran

git clone https://github.com/opencv/opencv.git
cd opencv
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..
make -j4
make install
