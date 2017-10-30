#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import base64
import numpy as np
import zlib


def code_data_base64(frame, compress=False, compress_level=6):
    a = b'\r\n'
    f = frame.tostring()
    print len(f)
    if compress:
        f = zlib.compress(f, compress_level)
    da = base64.b64encode(f)
    return da + a


def decode_frame(frame, image_height, image_width, color_pixel, error_msg='[Servidor]', uncompress=False):
    try:
        result = base64.decodestring(frame)
        if uncompress:
            result = zlib.decompress(result)
        frm = np.fromstring(result, dtype=np.uint8)
        frame_matrix = np.array(frm)
        if frame_matrix.shape[0] == image_height * image_width * color_pixel:
            frame_matrix = np.reshape(frame_matrix, (image_height, image_width, color_pixel))
            return True, frame_matrix
        else:
            return False, None
    except Exception as e:
        print("%s - Error: %s" % (error_msg, str(e)))
        return False, None


def code_frame2(frame, image_height, image_width, color_pixel):
    a = b'\r\n'
    f = frame.tostring()
    # if compress:
    #     f = zlib.compress(f, compress_level)
    lines = []
    for i in range(image_height):
        j = i * image_width
        k = i + image_width - 1
        da = base64.encodestring(f[j:k])
        lines.append(da + a)
    lines.append('!!!')   # end of frame
    return lines


def decode_frame2(frame_lines, image_height, image_width, color_pixel, error_msg='[Servidor]', uncompress=False):
    try:
        result = base64.decodestring(frame)
        if uncompress:
            result = zlib.decompress(result)
        frm = np.fromstring(result, dtype=np.uint8)
        frame_matrix = np.array(frm)
        if frame_matrix.shape[0] == image_height * image_width * color_pixel:
            frame_matrix = np.reshape(frame_matrix, (image_height, image_width, color_pixel))
            return True, frame_matrix
        else:
            return False, None
    except Exception as e:
        print("%s - Error: %s" % (error_msg, str(e)))
        return False, None

