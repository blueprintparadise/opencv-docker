#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import cv2
import socket
import argparse

from threading import Thread
from socket import timeout
import signal
from utils import signal_handler

import logging


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)
signal.signal(signal.SIGINT, signal_handler)
slow_mode = True  # default mode -- slow capture


def get_frame_rate(server_port, server_ip='0.0.0.0', max_num_connections=1):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((server_ip, server_port))
    connection.listen(max_num_connections)
    log.info("Waiting connections @ %d ..." % server_port)
    while True:
        (client_conn, (ip, port)) = connection.accept()
        result = client_conn.recv(1)
        if result != '':
            global slow_mode
            result = int(result)
            if result == 0:
                slow_mode = True
            if result == 1:
                slow_mode = False
            log.info("Setting to %s" % ('slow' if slow_mode else 'fast'))
        client_conn.close()


def send_image(frame_id, frame, timeout_socket, server_ip, server_port):
    """ send the frame to the image processing server """
    from utils import code_data_base64
    # format #1 - sends the entire image as a single block
    cod = code_data_base64(frame)

    # each image is sent on a different connection
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(timeout_socket)
    connection.connect((server_ip, server_port))
    log.info("Connecting to %s:%d" % (server_ip, server_port))
    try:
        connection.sendall(cod)
        log.debug("Frame %d sent" % frame_id)
    except timeout:
        global slow_mode
        slow_mode = True
    connection.close()


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

    parser.add_argument('--num-frames', type=int, default=30, help='number of skipped frames in slow mode')
    parser.add_argument('--num-frames-fast', type=int, default=10, help='number of skipped frames in fast mode')

    # parser.add_argument('--server-ip', type=str, default="localhost", help='server IP address that process images (default localhost)')
    parser.add_argument('--server-ip', type=str, default="192.168.1.100", help='server IP address that process images (default localhost)')
    parser.add_argument('--server-port', type=int, default=5500, help='server port')
    parser.add_argument('--videocapture-port', type=int, default=5501, help='video capture port')  # IP address is infered by the connection
    parser.add_argument('--timeout-socket', type=int, default=10, help='socket timeouf')

    parser.add_argument('--show-throughput', type=bool, default=False, help='if True, create a thread ')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.device_number)
    # cap = cv2.VideoCapture("/home/luis/Downloads/blade-runner-2049-trailer-4_h480p.mov")
    # cap = cv2.VideoCapture("/home/luis/Downloads/Avengers_2_trailer_3_51-1080p-HDTN.mp4")

    if args.show_throughput:
        from throughput import Throughput
        t = Throughput(interval=1.0)
        t.start()

    # to receive messages
    Thread(target=get_frame_rate,
           args=(),
           kwargs={'server_port': args.videocapture_port,
                   }
           ).start()

    ctrl_c = False
    frames = 0
    num_frames = 0
    frame_id = 0
    while not ctrl_c:
        try:
            ret, frame = cap.read()
            frame_id += 1  # identifies the frame
            frames += 1    # count number of frames in slow mode
            if (slow_mode and frames >= args.num_frames) or \
               (not slow_mode and frames >= args.num_frames_fast):
                frames = 0
                log.info("Send frame %d after - num frames %d" % (frame_id, args.num_frames if slow_mode else args.num_frames_fast))

                t = Thread(target=send_image, args=(),
                           kwargs={'frame_id': frame_id,
                                   'frame': frame,
                                   'timeout_socket': args.timeout_socket,
                                   'server_ip': args.server_ip,
                                   'server_port': args.server_port,
                                   }
                           )
                t.start()

            cv2.imshow('Actual capture', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                ctrl_c = True  # quitting
                break
        except Exception as e:
            print "Error: " + str(e)
            pass
    cap.release()
    if args.show_throughput:
        t.stop()
