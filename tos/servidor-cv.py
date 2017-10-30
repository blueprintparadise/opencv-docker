#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import sys
import socket
from threading import Thread
import cv2
import argparse
import pickle

from utils import decode_frame

import signal
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class ConnectionPool(Thread):

    def __init__(self,
                 ip,
                 port,
                 conn,
                 image_height,
                 image_width,
                 color_pixel,
                 ethanol_server_ip,
                 ethanol_server_port,
                 frames_in_fast_mode=50,
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
        self.frames_in_fast_mode = 0
        self.max_frames_in_fast_mode = frames_in_fast_mode
        self.slow_mode = True
        log.info("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def set_rate_ethanol(self, high_rate):
        if self.ethanol_server_ip is None:
            return
        obj = pickle.dumps(high_rate, protocol=0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ethanol_server_ip, self.ethanol_server_port))
        s.sendall(obj)

    def run(self):
        num = 0
        try:
            # Carrega o tipo de reconhecimento
            self.faceCascade = cv2.CascadeClassifier(self.cascPath)
            while True:
                try:
                    # Leitura do pacote
                    fileDescriptor = self.conn.makefile(mode='rb')
                    result = fileDescriptor.readline()
                    fileDescriptor.close()
                    if (len(result)) > 0:
                        # decodificacao
                        num += 1
                        log.debug("#%d frame received" % num)
                        ok, frame = decode_frame(result,
                                                 self.image_height,
                                                 self.image_width,
                                                 self.color_pixel,
                                                 error_msg='[Server]')
                        if (ok):
                            # converte a imagem em preto e branco para melhorar reconhecimento
                            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # detecta os objetos programados
                            try:
                                faces = self.faceCascade.detectMultiScale(
                                    gray_image,
                                    scaleFactor=1.1,
                                    minNeighbors=5,
                                    minSize=(30, 30)
                                )
                                if self.frames_in_fast_mode > 0:
                                    self.frames_in_fast_mode -= 1
                                if len(faces) > 0:
                                    log.info('has detected - #' + str(len(faces)))
                                    # RESET refresh time
                                    self.frames_in_fast_mode = self.max_frames_in_fast_mode
                                    self.slow_mode = False
                                    # 1 - camera
                                    self.conn.sendall('1\n')  # send to the camera a flag indicating detection
                                    # 2 - ethanol
                                    self.set_rate_ethanol(high_rate=True)
                                if self.frames_in_fast_mode == 0:  # and not self.slow_mode:
                                    log.info('returning to slow mode')
                                    self.slow_mode = True
                                    self.conn.sendall('0\n')  # send to the camera a flag indicating detection
                                    self.set_rate_ethanol(high_rate=True)

                            except Exception as e:
                                print(str(e))
                except Exception as e:
                    log.debug("[Err Server]  " + str(e))

        except Exception as e:
            log.debug("Connection lost: " + str(e))
        conn.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--image-height', type=int, default=480,
                        help='Image height in pixels')
    parser.add_argument('--image-width', type=int, default=640,
                        help='Image width in pixels')
    parser.add_argument('--color-pixel', type=int, default=3,
                        help='RGB')

    parser.add_argument('--server-ip', type=str, default="0.0.0.0",
                        help='server IP address that process images (default all)')
    parser.add_argument('--server-port', type=int, default=5500,
                        help='server port')
    parser.add_argument('--max-num-connections', type=int, default=20,
                        help='maximum number of connections')

    parser.add_argument('--ethanol-server-ip', type=str, default="150.164.10.52",
                        help='Ethanol server IP address')
    parser.add_argument('--ethanol-server-port', type=int, default=22222,
                        help='Ethanol server port')
    args = parser.parse_args()

    print("Waiting connections...")
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
                                ethanol_server_ip=None,  # args.ethanol_server_ip,
                                ethanol_server_port=args.ethanol_server_port,
                                )
        thread.start()
        # connection.close()
