#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import base64
import numpy as np
import zlib


def code_frame(frame, compress=False, compress_level=6):
    a = b'\r\n'
    f = frame.tostring()
    if compress:
        f = zlib.compress(f, compress_level)
    da = base64.b64encode(f)
    return da + a


def decode_frame(frame, image_height, image_width, color_pixel, error_msg='[Servidor]', uncompress=False):
    try:
        result = base64.b64decode(frame)
        if uncompress:
            result = zlib.decompress(result)
        frm = np.fromstring(result, dtype=np.uint8)
        frame_matrix = np.array(frm)
        frame_matrix = np.reshape(frame_matrix, (image_height, image_width, color_pixel))
        return True, frame_matrix
    except Exception as e:
        print("%s - Error: %s" % (error_msg, str(e)))
        return False, None
