#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import PIL.Image
import numpy

import common

with open('/dev/stdin', 'rb') as f:
    data = f.read()

if len(data) == 12 * 1920 * 1080:
    width = 1920
    height = 1080
elif len(data) % (12 * 576) == 0 and len(data) // (12 * 576) >= 720:
    width = len(data) // (12 * 576)
    height = 576
elif len(data) % (12 * 378) == 0 and len(data) // (12 * 378) >= 486:
    width = len(data) // (12 * 378)
    height = 378

yuvdata = numpy.ndarray((3, height, width), dtype='float32', buffer=bytearray(data))

try:
    COLORSPACE = common.ColorSpace(int(os.environ.get('COLORSPACE')))
except Exception:
    COLORSPACE = common.ColorSpace.BT709
LIMITED = bool(int(os.environ.get('LIMITED') or '0'))

if COLORSPACE is common.ColorSpace.BT601:
    convmatrix = numpy.array(
        [[1.0, 0.0, 1.402], [1.0, -0.34413628620102216, -0.7141362862010221], [1.0, 1.772, 0.0]])
elif COLORSPACE is common.ColorSpace.BT709:
    convmatrix = numpy.array(
        [[1.0, 0.0, 1.5748], [1.0, -0.18732427293064877, -0.4681242729306488], [1.0, 1.8556, 0.0]])

rgbdata = numpy.matvec(convmatrix, yuvdata, axes=[(0, 1), (0), (2)])

if LIMITED:
    rgbdata *= 219.0
    rgbdata += 16.0
else:
    rgbdata *= 255.0

rgbdata = numpy.round(numpy.minimum(numpy.maximum(rgbdata, 0.0), 255.0))

outbuf = bytearray(len(data) // 4)
output = numpy.ndarray((height, width, 3), dtype='uint8', buffer=outbuf)
output[:, :, :] = rgbdata

im = PIL.Image.frombuffer('RGB', (width, height), outbuf)
with open('/dev/stdout', 'wb') as f:
    im.save(f, format='PNG')
