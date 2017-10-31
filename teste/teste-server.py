#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import socket
import argparse


def read_lines(conn, ip, port):
    buffer_ = ''
    remainder_buff = ''
    connection_open = True
    while connection_open:
        try:
            i = buffer_.find('\n')
            if i >= 0:
                remainder_buff = buffer_[i + 1:]
                buffer_ = buffer_[:i]
            else:
                not_cr = True
                while not_cr:
                    data = conn.recv(4096)
                    if data == '':
                        connection_open = False
                        not_cr = False
                    else:
                        i = data.find('\n')
                        if i >= 0:
                            remainder_buff = data[i + 1:]
                            data = data[:i]
                            not_cr = False
                        buffer_ += data
            print "buffer: ", len(buffer_),
            print "resto : ", len(remainder_buff)
            buffer_ = remainder_buff
        except socket.error as e:
            print str(e)
            break


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
    parser.add_argument('--timeout-socket', type=int, default=10,
                        help='socket timeouf')
    args = parser.parse_args()

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((args.server_ip, args.server_port))
    connection.settimeout(args.timeout_socket)
    print "Servidor listen @", args.server_port
    connection.listen(args.max_num_connections)
    while True:
        (conn, (ip, port)) = connection.accept()
        print "Aceitou conexão de ", ip
        read_lines(conn, ip, port)
