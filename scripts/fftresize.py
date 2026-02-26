#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys

import PIL.Image
import numpy

import common


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Resize an image by performing a Discrete Fourier Transform resampling. The result is output to stdout as raw 16-bit RGB.')
    parser.add_argument('input_file', type=str,
                        help='Input file. May be any format supported by PIL or raw16:{width}x{height} in which case the data is read from stdin.')
    parser.add_argument('width', type=int, help='Target image width.')
    parser.add_argument('height', type=int, help='Target image height.')
    args = parser.parse_args(args)

    if not 'get_flattened_data' in PIL.Image.Image.__dict__.keys():
        PIL.Image.Image.get_flattened_data = PIL.Image.Image.getdata

    if args.input_file.startswith('raw16:'):
        width, height = (int(val) for val in args.input_file[6:].split('x'))
        with open('/dev/stdin', 'rb') as f:
            rawdata = f.read()
        data = numpy.ndarray((height, width, 3), dtype=numpy.uint16, buffer=rawdata)
    else:
        im = PIL.Image.open(args.input_file)
        if im.mode == 'P':
            im = im.convert(im.palette.mode)

        data = numpy.array(im.get_flattened_data())
        data = data.reshape((im.height, im.width, len(im.getbands())))
        if ';16' not in im.mode:
            data *= 256

    if args.width != data.shape[1]:
        data = common.resample_with_shift(data, args.width, axis=1)
    if args.height != data.shape[0]:
        data = common.resample_with_shift(data, args.height, axis=0)

    outbuf = bytearray(2 * numpy.prod(data.shape))
    output = numpy.ndarray(data.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:, :, :] = numpy.minimum(numpy.maximum(data, 0.0), 65535.0)

    with open('/dev/stdout', 'wb') as f:
        f.write(outbuf)


if __name__ == '__main__':
    sys.exit(_main(*sys.argv[1:]))
