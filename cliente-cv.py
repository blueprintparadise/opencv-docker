#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import cv2
import socket
from threading import Thread
from time import sleep
from _codecs import encode
import argparse

from utils import code_frame, decode_frame


class ConnectionSend(Thread):
    """thread to send message to the image processing server"""

    def __init__(self, conn_, device_):
        Thread.__init__(self)
        self.conn = conn_
        self.device = device_
        print("[+] New server socket thread started send")

    def run(self):
        ctrl_c = False
        while True and not ctrl_c:
            try:
                while True:
                    ret, frame = self.device.read()
                    _, cod = code_frame(frame)
                    self.conn.sendall(cod)
                    cv2.imshow('Janela de envio', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        ctrl_c = True  # quitting
                        break
            except Exception as e:
                print("Connection lost - sending data")


class ConnectionRec(Thread):
    """thread object to receive processed frame from server"""

    def __init__(self, conn_, image_height_, image_width_, color_pixel_):
        Thread.__init__(self)
        self.conn = conn_
        self.image_height = image_height_
        self.image_width = image_width_
        self.color_pixel = color_pixel_
        print("[+] New server socket thread started Rec")

    def run(self):
        ctrl_c = False
        while True and not ctrl_c:
            try:
                fileDescriptor = connection.makefile(mode='rb')
                result = fileDescriptor.readline()
                fileDescriptor.close()
                frame_matrix = decode_frame(result,
                                            self.image_height,
                                            self.image_width,
                                            self.color_pixel,
                                            error_msg='[Client]')
                if (len(frame_matrix.tostring()) > 0):
                    cv2.imshow('Janela de Recepcao', frame_matrix)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        ctrl_c = True  # quitting
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
    parser.add_argument('--timeout-socket', type=int, default=10,
                        help='socket timeouf')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.device_number)
    # cap = cv2.VideoCapture("/home/luis/Downloads/blade-runner-2049-trailer-4_h480p.mov")
    # cap = cv2.VideoCapture("/home/luis/Downloads/Avengers_2_trailer_3_51-1080p-HDTN.mp4")    

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(args.timeout_socket)
    connection.connect((args.server_ip, args.server_port))

    thread1 = ConnectionSend(connection, cap)
    thread1.start()
    thread2 = ConnectionRec(connection, args.image_height, args.image_width, args.color_pixel)
    thread2.start()

    threads = [thread1, thread2]
    for t in threads:
        t.join()
    cap.release()
    connection.close()
