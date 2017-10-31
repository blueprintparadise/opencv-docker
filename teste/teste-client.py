#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import socket
import argparse
import random

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

    parser.add_argument('--server-ip', type=str, default="localhost", help='server IP address that process images (default localhost)')
    # parser.add_argument('--server-ip', type=str, default="192.168.1.100", help='server IP address that process images (default localhost)')
    parser.add_argument('--server-port', type=int, default=5500,
                        help='server port')
    parser.add_argument('--timeout-socket', type=int, default=10,
                        help='socket timeouf')

    parser.add_argument('--show-throughput', type=bool, default=False, help='if True, create a thread ')
    args = parser.parse_args()

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.settimeout(args.timeout_socket)
    print "Cliente - connect"
    connection.connect((args.server_ip, args.server_port))

    s = ''
    crs = []
    for i in range(1000000):
        v = chr(i % 64 + 32)
        s += v
        if random.random() > 0.99999:
            s += '\n'
            if len(crs) == 0:
                tam = len(s) - 1
            else:
                tam = len(s) - (sum(crs) + len(crs) + 1)
            crs.append(tam)
    s += '\n'
    print "Client - sendall"
    connection.sendall(s)
    print "Enviado: ", len(s), "bytes"
    print "CRs    :", crs

    print "enviado connection close()"
    connection.close()
