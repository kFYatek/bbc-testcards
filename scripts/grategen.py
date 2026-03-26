#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import subprocess
import sys

import numpy


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Generate a frequency grating as a 1024x128 image. The output is written as a TIFF stream to the standard output.')
    parser.add_argument('sample_rate', type=float,
                        help='Sampling rate assumed for the target image.')
    parser.add_argument('frequency', type=float, help='Frequency of the grating.')
    parser.add_argument('minimum', type=float, help='Value for the lower tip of the grating.')
    parser.add_argument('maximum', type=float, help='Value for the lower tip of the grating.')
    parser.add_argument('start_phase', type=float, nargs='?', default=0.0,
                        help='Reference phase of the grating, where 0 is origin of a cosine, and integers correspond to a full period.')
    parser.add_argument('start_shift', type=float, nargs='?', default=0.0,
                        help='Position of the reference phase. 0 corresponds to sample #512 (counting from 0).')
    parser.add_argument('slope_freq', type=float, nargs='?',
                        help='Frequency of a function from which slopes of the grating are cut. Must be equal or greater than the grating frequency. If greater, the tops of the grating will be flattened to form a semi-square wave.')
    args = parser.parse_args(args)

    PHASE_FIRST = args.start_phase + 0.25 + (
            (-512.0 - args.start_shift) * args.frequency) / args.sample_rate
    PHASE_LAST = args.start_phase + 0.25 + (
            (511.0 - args.start_shift) * args.frequency) / args.sample_rate

    line = numpy.linspace(PHASE_FIRST, PHASE_LAST, 1024) % 1.0

    if args.slope_freq is None:
        pass
    elif args.slope_freq < args.frequency:
        raise Exception('Invalid slope frequency')
    elif args.slope_freq != args.frequency:
        slope = args.frequency / args.slope_freq
        for i in range(len(line)):
            if line[i] < 0.25 * slope:
                line[i] /= slope
            elif line[i] < 0.5 - 0.25 * slope:
                line[i] = 0.25
            elif line[i] < 0.5 + 0.25 * slope:
                line[i] = (line[i] - 0.5) / slope + 0.5
            elif line[i] < 1.0 - 0.25 * slope:
                line[i] = 0.75
            else:
                line[i] = (line[i] - 1.0) / slope + 1.0

    line = numpy.sin(line * 2.0 * numpy.pi)
    line = (line + 1.0) * 0.5 * (args.maximum - args.minimum) + args.minimum

    outbuf = bytearray(128 * 1024 * 8)
    output = numpy.ndarray((128, 1024), dtype=numpy.float64, buffer=outbuf)
    output[:] = line

    subprocess.run(
        ['magick', '-size', '1024x128', '-define', 'quantum:format=floating-point', '-depth', '64',
         'gray:-', 'tiff:-'], input=outbuf, check=True)


if __name__ == '__main__':
    sys.exit(_main(*sys.argv[1:]))
