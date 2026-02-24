#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import PIL.Image
import numpy

import common


def _main():
    target_width = int(sys.argv[2])
    target_height = int(sys.argv[3])

    if not 'get_flattened_data' in PIL.Image.Image.__dict__.keys():
        PIL.Image.Image.get_flattened_data = PIL.Image.Image.getdata

    if sys.argv[1].startswith('raw16:'):
        width, height = (int(val) for val in sys.argv[1][6:].split('x'))
        with open('/dev/stdin', 'rb') as f:
            rawdata = f.read()
        data = numpy.ndarray((height, width, 3), dtype=numpy.uint16, buffer=rawdata)
    else:
        im = PIL.Image.open(sys.argv[1])
        if im.mode == 'P':
            im = im.convert(im.palette.mode)

        data = numpy.array(im.get_flattened_data())
        data = data.reshape((im.height, im.width, len(im.getbands())))
        if ';16' not in im.mode:
            data *= 256

    if target_width != data.shape[1]:
        data = common.resample_with_mirrors(data, target_width, axis=1)
    if target_height != data.shape[0]:
        data = common.resample_with_mirrors(data, target_height, axis=0)

    outbuf = bytearray(2 * numpy.prod(data.shape))
    output = numpy.ndarray(data.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:, :, :] = numpy.minimum(numpy.maximum(data, 0.0), 65535.0)

    with open('/dev/stdout', 'wb') as f:
        f.write(outbuf)


if __name__ == '__main__':
    _main()
