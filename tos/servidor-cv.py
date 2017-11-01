#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import socket
from socket import timeout
from threading import Thread
import cv2
import argparse
import pickle

from utils import signal_handler, decode_frame
import signal

import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)
signal.signal(signal.SIGINT, signal_handler)

"""controlls the number of frames received by the ip address"""
frames_in_fast_mode = dict()


class ConnectionPool(Thread):

    def __init__(self,
                 ip,
                 port,
                 conn,
                 image_height,
                 image_width,
                 color_pixel,
                 ethanol_server_ip,
                 ethanol_server_port=5500,
                 videocapture_port=5501,
                 max_frames_in_fast_mode=200,
                 cascPath="./lbpcascade_frontalface.xml"):  # this must be an absolute path
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.image_height = image_height
        self.image_width = image_width
        self.color_pixel = color_pixel
        self.cascPath = cascPath
        self.ethanol_server_ip = ethanol_server_ip
        self.ethanol_server_port = ethanol_server_port
        self.max_frames_in_fast_mode = max_frames_in_fast_mode
        if ip not in frames_in_fast_mode:
            frames_in_fast_mode[ip] = 0
        self.videocapture_port = videocapture_port
        self.slow_mode = True
        log.debug("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def __del__(self):
        self.conn.close()  # close socket connection

    def set_rate_ethanol(self, high_rate):
        if self.ethanol_server_ip is None:
            return
        obj = pickle.dumps(high_rate, protocol=0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ethanol_server_ip, self.ethanol_server_port))
        s.sendall(obj)
        s.close()

    def set_frame_rate(self, value, videocapture_ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((videocapture_ip, self.videocapture_port))
        s.send(str(value))
        s.close()

    def run(self, buffer_size=4096):
        # Carrega o tipo de reconhecimento
        self.faceCascade = cv2.CascadeClassifier(self.cascPath)
        try:
            # read frame from socket
            # format #1 - sends the entire image as a single block
            result = ''
            data = self.conn.recv(buffer_size)
            while data != '':
                result += data
                data = self.conn.recv(buffer_size)

            if (len(result)) > 0:
                # decodificacao
                log.info("Frame received from %s:%d" % (self.ip, self.port))
                ok, frame = decode_frame(result,
                                         self.image_height,
                                         self.image_width,
                                         self.color_pixel,
                                         error_msg='[Server]')
                if (ok):
                    # converte a imagem em preto e branco para melhorar reconhecimento
                    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # detecta os objetos programados
                    faces = self.faceCascade.detectMultiScale(
                        gray_image,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )
                    global frames_in_fast_mode
                    if frames_in_fast_mode[self.ip] > 0:
                        frames_in_fast_mode[self.ip] -= 1
                    if len(faces) > 0:
                        # RESET refresh time
                        frames_in_fast_mode[self.ip] = self.max_frames_in_fast_mode
                        self.slow_mode = False
                        log.info('has detected - #%d - num frames reseted to %d' % (len(faces), self.max_frames_in_fast_mode))
                        # 1 - camera
                        # send to the camera a flag indicating detection
                        self.set_frame_rate(1, self.ip)
                        # 2 - ethanol
                        self.set_rate_ethanol(high_rate=True)
                    if frames_in_fast_mode[self.ip] == 0:  # and not self.slow_mode:
                        log.info('no detection - slow mode.')
                        self.slow_mode = True
                        # send to the camera a flag indicating NO detection
                        self.set_frame_rate(0, self.ip)
                        self.set_rate_ethanol(high_rate=False)
        except timeout:
            log.debug("Socket Timeout")
        except Exception as e:
            log.debug("Err Server: " + str(e))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--image-height', type=int, default=480, help='Image height in pixels')
    parser.add_argument('--image-width', type=int, default=640, help='Image width in pixels')
    parser.add_argument('--color-pixel', type=int, default=3, help='RGB')

    parser.add_argument('--frames-in-fast-mode', type=int, default=30, help='frames in fast mode')

    parser.add_argument('--videocapture-port', type=int, default=5501, help='video capture port')  # IP address is infered by the connection

    parser.add_argument('--server-ip', type=str, default="0.0.0.0", help='server IP address that process images (default all)')
    parser.add_argument('--server-port', type=int, default=5500, help='server port')
    parser.add_argument('--max-num-connections', type=int, default=20, help='maximum number of connections')

    # parser.add_argument('--ethanol-server-ip', type=str, default="150.164.10.52", help='Ethanol server IP address')
    parser.add_argument('--ethanol-server-ip', type=str, default=None, help=' ethanol.tos.usecase_tos server IP address')
    parser.add_argument('--ethanol-server-port', type=int, default=50000, help='ethanol.tos.usecase_tos server port')
    args = parser.parse_args()

    log.info("Waiting connections @ %s:%d ..." % (args.server_ip, args.server_port))
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((args.server_ip, args.server_port))
    connection.listen(args.max_num_connections)
    while True:
        (conn, (ip, port)) = connection.accept()
        thread = ConnectionPool(ip, port, conn,
                                args.image_height,
                                args.image_width,
                                args.color_pixel,
                                ethanol_server_ip=args.ethanol_server_ip,
                                ethanol_server_port=args.ethanol_server_port,
                                videocapture_port=args.videocapture_port,
                                max_frames_in_fast_mode=args.frames_in_fast_mode,
                                )
        thread.start()

    connection.close()  # this never happens
