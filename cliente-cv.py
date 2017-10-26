'''
Created on 5 de out de 2017

@author: luis
'''
import cv2
import socket
import base64
import numpy as np
from threading import Thread
from time import sleep
from _codecs import encode
import zlib

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

def codifica(frame):
    a = b'\r\n'    
    f = frame.tostring()
    da = base64.b64encode(f)
    return da + a    

def decodifica(frame):
    try:        
        result = base64.b64decode(frame)
        frm = np.fromstring(result, dtype=np.uint8)
        frame_matrix = np.array(frm)
        frame_matrix = np.reshape(frame_matrix, (IMAGE_HEIGHT, IMAGE_WIDTH, COLOR_PIXEL))
        return frame_matrix
    except Exception as e:
        print("[Cliente Error Envio] " + str(e.message))
        retun (frame_matrix=None)





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
                frame_matrix = decodifica(result)
                if (len(frame_matrix.tostring()) > 0):
                    cv2.imshow('Janela de Recepcao', frame_matrix)    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    
            except Exception as er:
                print("[Cliente Error Recepcao] " + str(er))



if __name__ == '__main__':
    # cap = cv2.VideoCapture(1)
    # cap = cv2.VideoCapture("/home/luis/Downloads/blade-runner-2049-trailer-4_h480p.mov")
    # cap = cv2.VideoCapture("/home/luis/Downloads/Avengers_2_trailer_3_51-1080p-HDTN.mp4")    
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(TIMEOUT_SOCKET)
    connection.connect((IP_SERVER, PORT_SERVER))
    
   
    thread1 = ConnectionSend(connection, cap)
    thread1.start()
    thread2 = ConnectionRec(connection)
    thread2.start()
    
    threads = []
    threads.append(thread1)
    threads.append(thread2)
    for t in threads:
        t.join()
    # connection.close()
    cap.release()            
  

    # connection.close()            
