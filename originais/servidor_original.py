'''
Created on 5 de out de 2017

@author: luis
'''
import time
import socket
import numpy as np
from threading import Thread
import cv2
from time import sleep
import datetime as dt
import base64
import zlib


SERVER_IP = "150.164.10.38"
SERVER_PORT = 5500
MAX_NUM_CONNECTIONS = 20
DEVICE_NUMBER = 0

IMAGE_HEIGHT = 480
IMAGE_WIDTH = 640

#IMAGE_HEIGHT = 360
#IMAGE_WIDTH = 848


COLOR_PIXEL = 3  # RGB

def codifica(frame):
    a = b'\r\n'
    f = frame.tostring()
    da = base64.b64encode(f)
    return da+a    

def decodifica(frame):
    try:
        result = base64.b64decode(frame)
        frm = np.fromstring(result, dtype=np.uint8)
        frame_matrix = np.array(frm)
        frame_matrix = np.reshape(frame_matrix, (IMAGE_HEIGHT, IMAGE_WIDTH, COLOR_PIXEL))
        return True,frame_matrix
    except Exception as e:
        print("[Servidor] " + str(e))
        return False,None


class ConnectionPool(Thread):

    def __init__(self, ip_, port_, conn_):
        Thread.__init__(self)
        self.ip = ip_
        self.port = port_
        self.conn = conn_        
        print("[+] New server socket thread started for " + self.ip + ":" + str(self.port))

    def run(self):
        try:
            # Carrega o tipo de reconhecimento
            cascPath = "/home/h3dema/opencv/data/lbpcascades/lbpcascade_frontalface.xml"
            faceCascade = cv2.CascadeClassifier(cascPath)

            while True:
                try:
                
                    # Leitura do pacote
                    fileDescriptor = self.conn.makefile(mode='rb')
                    result = fileDescriptor.readline()
                    fileDescriptor.close()
                    if (len(result)) >  0:
                        # decodificacao 
                        ok,frame = decodifica(result)
                        if (ok):
                            # converte a imagem em preto e branco para melhorar reconhecimento
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # detecta os objetos programados
                            faces = faceCascade.detectMultiScale(
                               gray,
                               scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(30, 30)
                            )
                            # Desenha os quadrados nos objetos encontrados
                            for (x, y, w, h) in faces:
                              cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                            
                            # Envia a figura modificada para o cliente
                            # #Codifica a imagem
                            cod = codifica(frame) 
                            # #Envia de volta
                            self.conn.sendall(cod)
                except Exception as e:
                    print("[Err Server]  " + str(e))
               
        except Exception as e:
            print("Conexao perdida " + str(e))
        conn.close()
            
if __name__ == '__main__':
    

    print("Waiting connections...")
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((SERVER_IP, SERVER_PORT))
    connection.listen(MAX_NUM_CONNECTIONS)
    while True:
        (conn, (ip, port)) = connection.accept()
        thread = ConnectionPool(ip, port, conn)
        thread.start()
    connection.close()

