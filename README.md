# opencv-docker

This repository creates a docker container with OpenCV.
It also contains our python files that create a client-server capturing images, that we use to test the network performance with Ethanol.

## Download

To download, build and run the docker container:
```
$ docker build -t opencv github.com/h3dema/opencv-docker
$ docker run -it opencv
```

## Inside the container

You need to create two containers. One for the client and one for the server.


```
# cd /src
# ls
```

# Without docker

If you don't want to run in a container, you can also install opencv directly into your computer.
Then you can clone this repository to your computer, and run the bash script *install.sh* that install OpenCV and its dependencies.


```
git clone https://github.com/h3dema/opencv-docker.git
cd opencv-docker
bash install.sh
```

Note: **You can install using python environments**, but this is beyond our scope.


# More info

See more in:
* https://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html
* https://docs.opencv.org/2.4/doc/tutorials/introduction/linux_install/linux_install.html.
