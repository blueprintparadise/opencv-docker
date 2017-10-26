#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import cv2
import socket
import base64
import numpy as np
from threading import Thread
from time import sleep
from _codecs import encode
import zlib
import argparse

from utils import codifica_frame, decodifica_frame

# IP_SERVER = "150.164.10.79"
IP_SERVER = "150.164.10.38"
PORT_SERVER = 5500
TIMEOUT_SOCKET = 10
SIZE_PACKAGE = 4096


IMAGE_HEIGHT = 480
IMAGE_WIDTH = 640

# IMAGE_HEIGHT = 360
# IMAGE_WIDTH = 848

COLOR_PIXEL = 3  # RGB


class ConnectionSend(Thread):

    def __init__(self, conn_, device_):
        Thread.__init__(self)

        self.conn = conn_
        self.device = device_
        print("[+] New server socket thread started send")

    def run(self):
        while(True):
            try:
                while True:
                    ret, frame = self.device.read()
                    cod = codifica(frame)                                        
                    self.conn.sendall(cod)                   
                    cv2.imshow('Janela de envio', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                       break
            except Exception as e:
                print("Conexao perdida Envio de Dados")


            

class ConnectionRec(Thread):

    def __init__(self, conn_):
        Thread.__init__(self)
        self.conn = conn_
        print("[+] New server socket thread started Rec")

    def run(self):
        while(True):
            try:
                fileDescriptor = connection.makefile(mode='rb')
                result = fileDescriptor.readline()                
                fileDescriptor.close()
                frame_matrix = decodifica_frame(RESULT,
                                                     self.image_height,
                                                     self.image_width,
                                                     self.color_pixel,
                                                     error_msg='[Cliente]')
                if (len(frame_matrix.tostring()) > 0):
                    cv2.imshow('Janela de Recepcao', frame_matrix)    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    
            except Exception as er:
                print("[Cliente Error Recepcao] " + str(er))



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--image-height', type=int, default=480,
                        help='Image height in pixels')
    parser.add_argument('--image-width', type=int, default=640,
                        help='Image width in pixels')
    parser.add_argument('--color-pixel', type=int, default=3,
                        help='RGB')
    parser.add_argument('--camera-id', dest="device_number", type=int, default=0,
                        help='RGB')

    parser.add_argument('--server-ip', type=str, default="localhost",
                        help='server IP address that process images (default localhost)')
    parser.add_argument('--server-port', type=int, default=5500,
                        help='server port')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.device_number)
    # cap = cv2.VideoCapture("/home/luis/Downloads/blade-runner-2049-trailer-4_h480p.mov")
    # cap = cv2.VideoCapture("/home/luis/Downloads/Avengers_2_trailer_3_51-1080p-HDTN.mp4")    

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(TIMEOUT_SOCKET)
    connection.connect((args.server_ip, args.server_port))
    
    thread1 = ConnectionSend(connection, cap)
    thread1.start()
    thread2 = ConnectionRec(connection)
    thread2.start()
    
    threads = []
    threads.append(thread1)
    threads.append(thread2)
    for t in threads:
        t.join()
    cap.release()
    connection.close()
