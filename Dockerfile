FROM ubuntu:14.04

RUN apt-get -y update && \
    apt-get -y upgrade
RUN apt-get -y install build-essential
RUN apt-get -y install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
RUN apt-get -y install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

RUN git clone https://github.com/opencv/opencv.git && \
    cd opencv && \
    mkdir release && \
    cd release && \
    cmake -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local ..

RUN mkdir /src
COPY cliente-cv.py /src/cliente-cv.py
COPY servidor-cv.py /src/servidor-cv.py

CMD cd /src && \
    /bin/bash
