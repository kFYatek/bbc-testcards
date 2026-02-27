#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import subprocess
import sys

import numpy

import common

def _main(*args):
    parser = argparse.ArgumentParser(
        description='Resize an image by performing a Discrete Fourier Transform resampling.')
    parser.add_argument('input_file', type=str,
                        help='Input file. May be any format supported by PIL or raw{16|float}:[filename@]{width}x{height} - if no filename is specified for raw, it\'s read from stdin.')
    parser.add_argument('width', type=int, help='Target image width.')
    parser.add_argument('height', type=int, help='Target image height.')
    parser.add_argument('output_file', type=str,
                        help='Output file name. Will be passed through to ImageMagick.')
    args = parser.parse_args(args)

    data, data_range = common.read_image(args.input_file)
    if data_range == 1:
        data = data * 56064.0 + 4096.0
    elif data_range == 255:
        data = data * 256.0
    else:
        assert data_range == 65535

    if args.width != data.shape[1]:
        data = common.resample_with_shift(data, args.width, axis=1)
    if args.height != data.shape[0]:
        data = common.resample_with_shift(data, args.height, axis=0)

    outbuf = bytearray(2 * numpy.prod(data.shape))
    output = numpy.ndarray(data.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:, :, :] = numpy.round(numpy.minimum(numpy.maximum(data, 0.0), 65535.0))

    subprocess.run(
        ['magick', '-size', f'{output.shape[1]}x{numpy.prod(output.shape[0])}', '-depth', '16',
         {1: 'gray:-', 3: 'rgb:-', 4: 'rgba:-'}[data.shape[2]], args.output_file], input=outbuf,
        check=True)


if __name__ == '__main__':
    sys.exit(_main(*sys.argv[1:]))
