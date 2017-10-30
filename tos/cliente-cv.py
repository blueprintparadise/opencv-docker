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
import argparse

from utils import code_frame
from socket import timeout

import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)


class ConnectionSend(Thread):
    """thread to send message to the image processing server"""

    def __init__(self, conn_, device_, num_frames=20):
        super(ConnectionSend, self).__init__()
        self.conn = conn_
        self.device = device_
        self.slow = True
        self.num_frames = num_frames
        log.info("[+] New server socket thread started send")

    def set_frame_rate(self, slow):
        log.info("setting to %s" % ('slow' if slow else 'fast'))
        self.slow = slow

    def run(self):
        ctrl_c = False
        frames = 0
        while True and not ctrl_c:
            while True:
                try:
                    ret, frame = self.device.read()
                    frames += 1
                    if self.slow:
                        if frames >= self.num_frames:
                            log.info("Send after - num frames %d" % self.num_frames)
                            cod = code_frame(frame)
                            self.conn.sendall(cod)
                            frames = 0
                    else:
                        cod = code_frame(frame)
                        self.conn.sendall(cod)

                    cv2.imshow('Actual capture', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        ctrl_c = True  # quitting
                        break
                except Exception as e:
                    log.debug("Connection lost - sending data - " + str(e))


class ConnectionRec(Thread):
    """thread object to receive if a person is detected"""

    def __init__(self, conn, thread1):
        super(ConnectionRec, self).__init__()
        self.conn = conn
        self.thread1 = thread1
        log.info("[+] New server socket thread started Rec")

    def run(self):
        ctrl_c = False
        while True and not ctrl_c:
            try:
                fileDescriptor = connection.makefile(mode='rb')
                result = fileDescriptor.readline()
                fileDescriptor.close()
                result = int(result.replace('\n', ''))
                if result == 0:
                    self.thread1.set_frame_rate(slow=True)
                    log.info("Returning to slow capture")
                if result == 1:
                    self.thread1.set_frame_rate(slow=False)
                    log.info("Detected a person")

            except timeout:
                # print("timeout")
                pass
            except Exception as er:
                log.debug("[ConnectionRec Error] " + str(er))


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

    # parser.add_argument('--server-ip', type=str, default="localhost", help='server IP address that process images (default localhost)')
    parser.add_argument('--server-ip', type=str, default="192.168.1.100", help='server IP address that process images (default localhost)')
    parser.add_argument('--server-port', type=int, default=5500,
                        help='server port')
    parser.add_argument('--timeout-socket', type=int, default=10,
                        help='socket timeouf')

    parser.add_argument('--show-throughput', type=bool, default=False, help='if True, create a thread ')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.device_number)
    # cap = cv2.VideoCapture("/home/luis/Downloads/blade-runner-2049-trailer-4_h480p.mov")
    # cap = cv2.VideoCapture("/home/luis/Downloads/Avengers_2_trailer_3_51-1080p-HDTN.mp4")

    # connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(args.timeout_socket)
    connection.connect((args.server_ip, args.server_port))

    thread1 = ConnectionSend(connection, cap)
    thread1.start()
    thread2 = ConnectionRec(connection, thread1)
    thread2.start()

    if args.show_throughput:
        from throughput import Throughput
        t = Throughput(interval=1.0)
        t.start()

    threads = [thread1, thread2]
    for t in threads:
        t.join()
    cap.release()
    connection.close()

    if args.show_throughput:
        t.stop()
