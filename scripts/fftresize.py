#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import subprocess
import sys

import PIL.Image
import numpy

import common

if not 'get_flattened_data' in PIL.Image.Image.__dict__.keys():
    PIL.Image.Image.get_flattened_data = PIL.Image.Image.getdata


def read_image(filename: str) -> numpy.ndarray:
    if filename.startswith('raw16:'):
        args = filename[6:]
        if '@' in args:
            filename, args = args.split('@', 1)
        else:
            filename = '/dev/stdin'
        width, height = (int(val) for val in args.split('x'))
        with open(filename, 'rb') as f:
            rawdata = f.read()
        data = numpy.ndarray((height, width, 3), dtype=numpy.uint16, buffer=rawdata)
    else:
        im = PIL.Image.open(filename)
        if im.mode == 'P':
            im = im.convert(im.palette.mode)

        data = numpy.array(im.get_flattened_data())
        data = data.reshape((im.height, im.width, len(im.getbands())))
        if ';16' not in im.mode:
            data *= 256
    return data


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Resize an image by performing a Discrete Fourier Transform resampling.')
    parser.add_argument('input_file', type=str,
                        help='Input file. May be any format supported by PIL or raw16:[filename@]{width}x{height} - if no filename is specified for raw16, it\'s read from stdin.')
    parser.add_argument('width', type=int, help='Target image width.')
    parser.add_argument('height', type=int, help='Target image height.')
    parser.add_argument('output_file', type=str,
                        help='Output file name. Will be passed through to ImageMagick.')
    args = parser.parse_args(args)

    data = read_image(args.input_file)

    if args.width != data.shape[1]:
        data = common.resample_with_shift(data, args.width, axis=1)
    if args.height != data.shape[0]:
        data = common.resample_with_shift(data, args.height, axis=0)

    outbuf = bytearray(2 * numpy.prod(data.shape))
    output = numpy.ndarray(data.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:, :, :] = numpy.minimum(numpy.maximum(data, 0.0), 65535.0)

    subprocess.run(
        ['magick', '-size', f'{output.shape[1]}x{numpy.prod(output.shape[0])}', '-depth', '16',
         {1: 'gray:-', 3: 'rgb:-', 4: 'rgba:-'}[data.shape[2]], args.output_file], input=outbuf,
        check=True)


if __name__ == '__main__':
    sys.exit(_main(*sys.argv[1:]))
