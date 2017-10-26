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
    make install

#RUN apt-get -y install doxygen && \
#    cd /opencv/build/doc/ && \
#    make -j4 doxygen

RUN git clone https://github.com/opencv/opencv_extra.git

RUN mkdir /src
COPY cliente-cv.py /src/cliente-cv.py
COPY servidor-cv.py /src/servidor-cv.py
COPY utils.py /src/utils.py

# to export GUI
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer
ENV DISPLAY :0
USER developer
ENV HOME /home/developer
RUN sudo chown -R developer /src /opencv

# hack for libdc1394-22-dev
# ref. https://stackoverflow.com/questions/29274638/opencv-libdc1394-error-failed-to-initialize-libdc1394
CMD sudo ln /dev/null /dev/raw1394 && \
    cd /src && \
    /bin/bash
