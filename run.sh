#!/bin/bash

###
# download and create de container
###
# git clone https://github.com/h3dema/opencv-docker.git
# cd opencv-docker
# docker build -t opencv .

# set variables
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

###
# run the container
###
docker run -ti -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -e DISPLAY=$DISPLAY -e XAUTHORITY=$XAUTH opencv
