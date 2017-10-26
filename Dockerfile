FROM ubuntu:14.04

RUN apt-get -y update && \
    apt-get -y upgrade
RUN apt-get -y install build-essential
RUN apt-get -y install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
RUN apt-get -y install libgtk-3-dev
RUN apt-get -y install libxvidcore-dev libx264-dev
RUN apt-get -y install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
RUN apt-get -y install libjpeg8-dev libtiff5-dev libpng12-dev
RUN apt-get -y install libatlas-base-dev gfortran

RUN git clone https://github.com/opencv/opencv.git && \
    cd opencv && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local .. && \
    make -j4 && \
    pushd . ** \
    cd build/doc/ && \
    make -j4 doxygen && \
    popd && \
    make install

RUN git clone https://github.com/opencv/opencv_extra.git

RUN mkdir /src
COPY cliente-cv.py /src/cliente-cv.py
COPY servidor-cv.py /src/servidor-cv.py

CMD cd /src && \
    /bin/bash
