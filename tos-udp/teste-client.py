#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import socket
from math import ceil
import logging
from socket import timeout
from socket import error as socket_error
import errno

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
log = logging.getLogger(__file__)


timeout_socket = 10
chunk_size = 1200
server_ip = '150.164.10.22'
server_port = 5000

# each image is sent on a different connection
TAMANHO = 1228800      # tamanho de uma imagem do videocapture (480x640)
TAMANHO = 130000       # com este tamanho já está dando falhas que na maioria das vezes não consegue recuperar o conteudo completo do outro lado
cod = 'a' * (TAMANHO)  # gera uma string com a's
cod += '\r\n'

for frame_id in range(10):
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sizes = []
    try:
        n = int(ceil(float(len(cod)) / chunk_size))
        for i in range(n):
            b = i * chunk_size
            msg = cod[b:b + chunk_size]
            sizes.append(len(msg))
            connection.sendto(msg, (server_ip, server_port))
        log.info("Frame %d sent to %s:%d - size: %d" % (frame_id, server_ip, server_port, len(cod)))
        log.info("chunk_size: %d - last chunk_size: %d - num chunks: %d - total size: %d" % (chunk_size, sizes[-1], len(sizes), sum(sizes)))
    except timeout:
        global slow_mode
        slow_mode = True
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            log.info("Connection refused")
    connection.close()
    print "fim da transmissão - %d" % frame_id

    import time
    time.sleep(1)