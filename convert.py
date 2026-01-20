#!/usr/bin/env python3
import os
import numpy

import PIL
import PIL.Image

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

chlen = len(data) // 3

ydata = data[:chlen]
udata = data[chlen:2*chlen]
vdata = data[2*chlen:3*chlen]

y = numpy.ndarray((height, width), dtype='float32', buffer=bytearray(ydata))
u = numpy.ndarray((height, width), dtype='float32', buffer=bytearray(udata))
v = numpy.ndarray((height, width), dtype='float32', buffer=bytearray(vdata))

COLORSPACE=int(os.environ.get('COLORSPACE') or '709')
LIMITED=int(os.environ.get('LIMITED') or '0')

if COLORSPACE == 601:
    r = y + 1.402 * v
    g = y - 0.34413628620102216 * u - 0.7141362862010221 * v
    b = y + 1.772 * u
elif COLORSPACE == 709:
    r = y + 1.5748 * v
    g = y - 0.18732427293064877 * u - 0.4681242729306488 * v
    b = y + 1.8556 * u

if LIMITED > 0:
    r = 219.0 * r + 16.0
    g = 219.0 * g + 16.0
    b = 219.0 * b + 16.0
else:
    r = 255.0 * r
    g = 255.0 * g
    b = 255.0 * b

r = numpy.round(numpy.minimum(numpy.maximum(r, 0.0), 255.0))
g = numpy.round(numpy.minimum(numpy.maximum(g, 0.0), 255.0))
b = numpy.round(numpy.minimum(numpy.maximum(b, 0.0), 255.0))

outbuf = bytearray(len(data) // 4)
output = numpy.ndarray((height, width, 3), dtype='uint8', buffer=outbuf)
output[:, :, 0] = r
output[:, :, 1] = g
output[:, :, 2] = b

im = PIL.Image.frombuffer('RGB', (width, height), outbuf)
with open('/dev/stdout', 'wb') as f:
    im.save(f, format='PNG')
