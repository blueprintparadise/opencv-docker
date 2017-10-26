#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import base64
import numpy as np


def codifica_frame(frame):
    a = b'\r\n'
    f = frame.tostring()
    da = base64.b64encode(f)
    return da + a


def decodifica_frame(frame, image_height, image_width, color_pixel, error_msg='[Servidor]'):
    try:
        result = base64.b64decode(frame)
        frm = np.fromstring(result, dtype=np.uint8)
        frame_matrix = np.array(frm)
        frame_matrix = np.reshape(frame_matrix, (image_height, image_width, color_pixel))
        return True, frame_matrix
    except Exception as e:
        print("%s - Error: " % (error_msg, str(e)))
        return False, None
