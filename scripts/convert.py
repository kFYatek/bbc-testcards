#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys

import numpy

import common


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Convert an initially preprocessed image to a more usable format.')
    parser.add_argument('input_file', type=str,
                        help='Input file. May be any format supported by PIL or raw{16|float}:[filename@]{width}x{height} - if no filename is specified for raw, it\'s read from stdin.')
    parser.add_argument('--input-colorspace', type=lambda x: common.ColorSpace(int(x)),
                        help=f'Color space to use when converting input to YUV {list(common.ColorSpace)}. Default is BT.601 for PIL input and YUV for raw input.')
    parser.add_argument('--output-colorspace', type=lambda x: common.ColorSpace(int(x)),
                        default=common.ColorSpace.BT601,
                        help=f'Color space to use when converting to RGB on output {list(common.ColorSpace)}.')
    parser.add_argument('--card', type=int,
                        help='Test card number from common.py. Scaling and shifting will be applied accordingly if provided.')
    parser.add_argument('--scale', type=lambda x: common.ScalingMode(int(x)),
                        default=common.ScalingMode.NONE,
                        help=f'Scaling mode to use {list(common.ScalingMode)}.')
    parser.add_argument('output_file', type=str,
                        help='Output file. May be any format supported by ImageMagick or raw16:[filename] (stdout by default).')
    parser.add_argument('--fullrange', action='store_true',
                        help='Use full (0..65535) instead of limited/video (4096..60160) range on output.')
    args = parser.parse_args(args)

    yuvdata = common.load_and_process_image(args.input_file, args.input_colorspace).transpose(
        (2, 0, 1))
    width = yuvdata.shape[2]
    height = yuvdata.shape[1]

    dimensions = None
    src_left = 0.0
    src_top = 0.0
    if args.card is not None:
        dimensions = common.get_scaling_dimensions(args.scale, common.CARDS[args.card].mode)
        if width >= common.get_scaling_dimensions(common.ScalingMode.VERTICAL,
                                                  common.CARDS[args.card].mode).crop_w:
            src_left = common.CARDS[args.card].src_left
        if height == 1080:
            src_top = common.CARDS[args.card].src_top

    if dimensions is not None:
        while dimensions.precrop_w > yuvdata.shape[2]:
            flipped = numpy.flip(yuvdata, axis=2)
            yuvdata = numpy.concatenate([flipped, yuvdata, flipped], axis=2)
        if dimensions.precrop_w != yuvdata.shape[2]:
            yuvdata = yuvdata[:, :, (yuvdata.shape[2] - dimensions.precrop_w) // 2:]
            yuvdata = yuvdata[:, :, :dimensions.precrop_w]
        src_left += yuvdata.shape[2] / (2 * dimensions.scale_w) - 0.5
        src_top += yuvdata.shape[1] / (2 * dimensions.scale_h) - 0.5

    yuvdata = common.apply_shift(yuvdata, src_left, axis=2)
    yuvdata = common.apply_shift(yuvdata, src_top, axis=1)

    if dimensions is not None:
        yuvdata = common.resample_with_mirrors(yuvdata, dimensions.scale_w, axis=2)
        yuvdata = common.resample_with_mirrors(yuvdata, dimensions.scale_h, axis=1)
        if dimensions.crop_w != dimensions.scale_w:
            yuvdata = yuvdata[:, :, (yuvdata.shape[2] - dimensions.crop_w) // 2:]
            yuvdata = yuvdata[:, :, :dimensions.crop_w]

    outdata = numpy.matvec(args.output_colorspace.to_rgb_matrix, yuvdata, axes=[(0, 1), 0, 0])

    raw16out = args.output_file.startswith('raw16:')
    if raw16out:
        format_name, output_file = args.output_file.split(':', 1)
        if output_file == '':
            output_file = '/dev/stdout'
    else:
        output_file = args.output_file
    if args.fullrange:
        if args.output_colorspace is common.ColorSpace.YUV:
            outdata[1:] += 0.5
        outdata *= 65535.0
    else:
        if args.output_colorspace is not common.ColorSpace.YUV:
            outdata *= 219.0
            outdata += 16.0
        else:
            outdata[0] *= 219.0
            outdata[0] += 16.0
            outdata[1:] *= 224.0
            outdata[1:] += 128.0
        outdata *= 256.0

    outdata = numpy.transpose(outdata, (1, 2, 0))
    outbuf = bytearray(outdata.size * 2)
    output = numpy.ndarray(outdata.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:, :, :] = numpy.round(numpy.minimum(numpy.maximum(outdata, 0.0), 65535.0))

    if raw16out:
        with open(output_file, 'wb') as f:
            f.write(outbuf)
    else:
        command = ['magick', '-size', f'{output.shape[1]}x{output.shape[0]}', '-depth', '16',
                   'rgb:-']
        iccfile = None
        if not args.fullrange:
            if args.output_colorspace is common.ColorSpace.GRAYSCALE:
                iccfile = 'ITU-1886-gray-video16-v4.icc'
            elif args.output_colorspace is common.ColorSpace.BT601:
                if output.shape[0] in range(480, 487):
                    iccfile = 'ITU-601-525-video16-v4.icc'
                else:
                    iccfile = 'ITU-601-625-video16-v4.icc'
            elif args.output_colorspace is common.ColorSpace.BT709:
                iccfile = 'ITU-709-video16-v4.icc'
        if iccfile is not None:
            command += ['+profile', 'icc', '-profile',
                        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     iccfile)]
        if args.output_colorspace is common.ColorSpace.GRAYSCALE:
            command += ['-define', 'png:color-type=0']
        else:
            command += ['-define', 'png:color-type=2']
        command += [output_file]

        subprocess.run(command, input=outbuf, check=True)


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
