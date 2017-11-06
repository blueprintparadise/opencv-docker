#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''
Created on 5 de out de 2017

@author: luis
@author: h3dema
'''
import socket
from socket import timeout
import cv2
import argparse
import pickle
from socket import error as socket_error
import errno

from utils import signal_handler, decode_frame
import signal

import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)
signal.signal(signal.SIGINT, signal_handler)

"""controlls the number of frames received by the ip address"""
frames_in_fast_mode = dict()
slow_mode = dict()
num_frames = dict()

cascPath = "./lbpcascade_frontalface.xml"  # this must be an absolute path


def set_rate_ethanol(ethanol_server_ip, ethanol_server_port, high_rate, timeout_socket=10):
    if ethanol_server_ip is None:
        return
    obj = pickle.dumps(high_rate, protocol=0)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_socket)
    try:
        s.connect((ethanol_server_ip, ethanol_server_port))
        log.info("ETHANOL: rate to %s" % ("high" if high_rate else "slow"))
        s.sendall(obj)
    except timeout:
        log.info("timeout - did't inform that rate is %d to the ethanol server" % high_rate)
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            log.debug("set_rate_ethanol - Connection refused by %s" % ethanol_server_ip)
    s.close()


def set_frame_rate(value, videocapture_ip, videocapture_port=5501, timeout_socket=10):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_socket)
    try:
        s.connect((videocapture_ip, videocapture_port))
        s.send(str(value))
        log.info("Set rate to %d in %s:%d" % (value, videocapture_ip, videocapture_port))
    except timeout:
        log.info("timeout - did't configure that rate is %d in %s:%d" % (value, videocapture_ip, videocapture_port))
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            log.debug("set_frame_rate- Connection refused by %s" % videocapture_ip)
    s.close()


def process_image(client, videocapture_port,
                  img, image_height, image_width, color_pixel, max_frames_in_fast_mode,
                  ethanol_server_ip, ethanol_server_port):
    global frames_in_fast_mode, slow_mode
    # decodificacao
    ip, port = client
    log.info("Frame received from %s:%d - size %d - mode: %s" % (ip, port, len(img), "slow" if frames_in_fast_mode[ip] == 0 else "high"))
    ok, frame = decode_frame(img,
                             image_height,
                             image_width,
                             color_pixel,
                             error_msg='[Server]')
    if (ok):
        # converte a imagem em preto e branco para melhorar reconhecimento
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detecta os objetos programados
        faceCascade = cv2.CascadeClassifier(cascPath)
        try:
            faces = faceCascade.detectMultiScale(
                gray_image,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
        except Exception as e:
            log.debug("Err Server: " + str(e))
            faces = 0
        if frames_in_fast_mode[ip] > 0:
            frames_in_fast_mode[ip] -= 1
        if len(faces) > 0:
            # RESET refresh time
            frames_in_fast_mode[ip] = max_frames_in_fast_mode
            slow_mode[ip] = False
            log.info('has detected - #%d - num frames reseted to %d' % (len(faces), max_frames_in_fast_mode))
            # 1 - camera
            # send to the camera a flag indicating detection
            set_frame_rate(value=1, videocapture_ip=ip, videocapture_port=videocapture_port)
            # 2 - ethanol
            set_rate_ethanol(ethanol_server_ip, ethanol_server_port, high_rate=True)
        if frames_in_fast_mode[ip] == 0:  # and not self.slow_mode:
            log.info('No detection - slow mode.')
            slow_mode[ip] = True
            # send to the camera a flag indicating NO detection
            set_frame_rate(value=0, videocapture_ip=ip, videocapture_port=videocapture_port)
            set_rate_ethanol(ethanol_server_ip, ethanol_server_port, high_rate=False)


def process_buffer(img, data,
                   image_height, image_width, color_pixel, max_frames_in_fast_mode,
                   client, videocapture_port,
                   ethanol_server_ip, ethanol_server_port):
    if data == '':
        process_image(client=client,
                      videocapture_port=videocapture_port,
                      img=img,
                      image_height=image_height,
                      image_width=image_width,
                      color_pixel=color_pixel,
                      max_frames_in_fast_mode=max_frames_in_fast_mode,
                      ethanol_server_ip=ethanol_server_ip,
                      ethanol_server_port=ethanol_server_port,
                      )
        img = ''
    else:
        i = data.find('\n')
        if i >= 0:
            img += data[:i + 1]
            log.debug("frames recv: %d" % (num_frames[client] + 1))
            process_image(client=client,
                          videocapture_port=videocapture_port,
                          img=img,
                          image_height=image_height,
                          image_width=image_width,
                          color_pixel=color_pixel,
                          max_frames_in_fast_mode=max_frames_in_fast_mode,
                          ethanol_server_ip=ethanol_server_ip,
                          ethanol_server_port=ethanol_server_port,
                          )
            img = data[i + 1:]
            num_frames[client] = 1 if len(img) > 0 else 0
        else:
            img += data
            num_frames[client] += 1
            # print "client", client, "frames", num_frames[client]
    return img


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--image-height', type=int, default=480, help='Image height in pixels')
    parser.add_argument('--image-width', type=int, default=640, help='Image width in pixels')
    parser.add_argument('--color-pixel', type=int, default=3, help='RGB')

    parser.add_argument('--frames-in-fast-mode', type=int, default=30, help='frames in fast mode')

    parser.add_argument('--videocapture-port', type=int, default=5501, help='video capture port')  # IP address is infered by the connection

    parser.add_argument('--server-ip', type=str, default="0.0.0.0", help='server IP address that process images (default all)')
    # parser.add_argument('--server-ip', type=str, default="150.164.10.22", help='server IP address that process images (default all)')
    # parser.add_argument('--server-ip', type=str, default="192.168.1.100", help='server IP address that process images (default all)')
    parser.add_argument('--server-port', type=int, default=5000, help='server port')
    parser.add_argument('--max-num-connections', type=int, default=20, help='maximum number of connections')

    parser.add_argument('--ethanol-server-ip', type=str, default="150.164.10.52", help='Ethanol server IP address')
    # parser.add_argument('--ethanol-server-ip', type=str, default=None, help=' ethanol.tos.usecase_tos server IP address')
    parser.add_argument('--ethanol-server-port', type=int, default=50000, help='ethanol.tos.usecase_tos server port')
    args = parser.parse_args()

    log.info("Waiting connections @ %s:%d ..." % (args.server_ip, args.server_port))
    log.info("Expected Image size %d x %d x %d " % (args.image_height, args.image_width, args.color_pixel))
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((args.server_ip, args.server_port))
    recv_buffer = dict()
    while True:
        (msg, orig) = connection.recvfrom(2048)
        log.debug("message with %d bytes received from %s:%d" % (len(msg), orig[0], orig[1]))
        ip, port = orig
        if orig not in recv_buffer:
            recv_buffer[orig] = ''
        if orig not in num_frames:
            num_frames[orig] = 0
        if ip not in frames_in_fast_mode:
            frames_in_fast_mode[ip] = 0
        recv_buffer[orig] = process_buffer(client=orig,
                                           videocapture_port=args.videocapture_port,
                                           img=recv_buffer[orig],
                                           data=msg,
                                           image_height=args.image_height,
                                           image_width=args.image_width,
                                           color_pixel=args.color_pixel,
                                           max_frames_in_fast_mode=args.frames_in_fast_mode,
                                           ethanol_server_ip=args.ethanol_server_ip,
                                           ethanol_server_port=args.ethanol_server_port,
                                           )

    connection.close()  # this never happens
