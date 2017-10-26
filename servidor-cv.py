#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import time
import socket
from threading import Thread
import cv2
from time import sleep
import datetime as dt
import zlib
import argparse

from utils import codifica_frame, decodifica_frame


class ConnectionPool(Thread):

    def __init__(self, ip_, port_, conn_, image_height_, image_width_, color_pixel_):
        Thread.__init__(self)
        self.ip = ip_
        self.port = port_
        self.conn = conn_
        self.image_height = image_height_
        self.image_width = image_width_
        self.color_pixel = color_pixel_
        print("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

        # Carrega o tipo de reconhecimento
        cascPath = "/home/luis/opencv/opencv/data/lbpcascades/lbpcascade_frontalface.xml"
        self.faceCascade = cv2.CascadeClassifier(cascPath)

    def run(self):
        try:
            while True:
                try:
                    # Leitura do pacote
                    fileDescriptor = self.conn.makefile(mode='rb')
                    result = fileDescriptor.readline()
                    fileDescriptor.close()
                    if (len(result)) > 0:
                        # decodificacao
                        ok, frame = decodifica_frame(result,
                                                     self.image_height,
                                                     self.image_width,
                                                     self.color_pixel,
                                                     error_msg='[Servidor]')
                        if (ok):
                            # converte a imagem em preto e branco para melhorar reconhecimento
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # detecta os objetos programados
                            faces = self.faceCascade.detectMultiScale(
                                gray,
                                scaleFactor=1.1,
                                minNeighbors=5,
                                minSize=(30, 30)
                            )
                            # Desenha os quadrados nos objetos encontrados
                            for (x, y, w, h) in faces:
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            # Envia a figura modificada para o cliente
                            # codifica a imagem
                            cod = codifica_frame(frame)
                            # #Envia de volta
                            self.conn.sendall(cod)
                except Exception as e:
                    print("[Err Server]  " + str(e))

        except Exception as e:
            print("Conexao perdida " + str(e))
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
    args = parser.parse_args()

    print("Waiting connections...")
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((args.server_ip, args.server_port))
    connection.listen(args.max_num_connections)
    while True:
        (conn, (ip, port)) = connection.accept()
        thread = ConnectionPool(ip, port, conn, args.image_height, args.image_width, args.color_pixel)
        thread.start()
    # connection.close()
