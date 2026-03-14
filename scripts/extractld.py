#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import math
import os
import subprocess
import sys

import numpy
import scipy.fft
import scipy.signal

import common


def mean_with_outliers(data, max_delta=0.25):
    result = numpy.mean(data, axis=0)
    if data.shape[0] > 1:
        deltas = numpy.abs(data - result)
        valid_values = (deltas <= ((max_delta * (data.shape[0] - 1)) / data.shape[0]))
        result = numpy.sum(data * valid_values, axis=0) / numpy.sum(valid_values, axis=0)
        result[~numpy.isfinite(result)] = 0.0
    return result


def deghost(data, shift, weight):
    return (data - common.resample(data, shift=shift, axis=-1, pad_mode='edge') * weight) / (
            1.0 - weight)


def half_freqs(data):
    data = numpy.swapaxes(data, 0, len(data.shape) - 1)
    fft = scipy.fft.rfft(data, axis=0)
    fft[fft.shape[0] // 2:] = 0.0
    data = scipy.fft.irfft(fft, n=data.shape[0], axis=0)
    return numpy.swapaxes(data, 0, len(data.shape) - 1)


def deqam(data):
    cosine = numpy.array(([1.0, 0.0, -1.0, 0.0] * math.ceil(data.shape[-1] / 4))[:data.shape[-1]])
    sine = numpy.array(([0.0, 1.0, 0.0, -1.0] * math.ceil(data.shape[-1] / 4))[:data.shape[-1]])
    chroma_u = half_freqs(sine * data)
    chroma_v = half_freqs(cosine * data)
    return chroma_u + 1.0j * chroma_v


def depal(chroma):
    burst_angles = numpy.angle(numpy.mean(chroma[:, :, 109:129], axis=-1))
    burst_phases = (burst_angles[:, 167] - burst_angles[:, 166] + numpy.pi) % (
            2.0 * numpy.pi) - numpy.pi
    burst_mask = abs(burst_phases) < 0.4968 * numpy.pi
    palmask = numpy.ones(chroma.shape, dtype=numpy.bool)
    palmask[burst_mask] = ~palmask[burst_mask]
    palmask[:, 1::2] = ~palmask[:, 1::2]
    chroma = chroma.transpose((2, 0, 1))
    chroma = chroma * numpy.exp(1.0j * (0.75 * numpy.pi - burst_angles))
    chroma = chroma.transpose((1, 2, 0))
    chroma[palmask] = -numpy.imag(chroma[palmask]) - 1.0j * numpy.real(chroma[palmask])
    return chroma


def deinterlace(data):
    output = numpy.ndarray(data.shape, dtype=data.dtype)
    output[0::2] = data[:data.shape[0] // 2]
    output[1::2] = data[data.shape[0] // 2:]
    return output


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Decode a still image from multiple frames of TBC information decoded using ld-decode. For now, only supports PAL CAV Laserdisc sources.')
    parser.add_argument('input_file', type=str,
                        help='TBC file to read data from. A matching *.json file is required too.')
    parser.add_argument('output_file', type=str,
                        help='Output file name. Will be passed through to ImageMagick.')
    parser.add_argument('start_frame', type=int, nargs='?',
                        help='CAV frame number of the first frame the image to decode appears on. Default is the first frame of input.')
    parser.add_argument('frame_count', type=int, nargs='?',
                        help='Number of frames the still image appears on. Must be at least 4. Default is all the frames.')
    parser.add_argument('--black-level', type=float,
                        help='Black level (on a 16-bit sample scale) to use instead of the one declared in metadata')
    parser.add_argument('--white-level', type=float,
                        help='White level (on a 16-bit sample scale) to use instead of the one declared in metadata')
    parser.add_argument('--deghost', type=float, nargs=2,
                        help='Enable deghosting. Provide shift (in samples at 4fSC) and weight values as arguments')
    parser.add_argument('--u-scale', type=float, help='Multiplier for the U color component')
    parser.add_argument('--v-scale', type=float, help='Multiplier for the V color component')
    parser.add_argument('--shift', type=float,
                        help='Number of samples (at 4fSC, possibly fractional) to shift the image by')
    args = parser.parse_args(args)

    with open(args.input_file + '.json') as f:
        metadata = json.load(f)

    if metadata['videoParameters']['system'] == 'PAL':
        assert metadata['videoParameters']['fieldWidth'] == 1135
        assert metadata['videoParameters']['fieldHeight'] == 313
    else:
        assert metadata['videoParameters']['system'] == 'NTSC'
        assert metadata['videoParameters']['fieldWidth'] == 910
        assert metadata['videoParameters']['fieldHeight'] == 263
        raise Exception('NTSC is not yet supported')

    input_file_first_field = 0

    with open(args.input_file, 'rb') as f:
        if args.start_frame is not None:
            fields = iter(metadata['fields'])
            field = next(fields)
            if not field['isFirstField']:
                input_file_first_field -= 1
                field = next(fields)
            assert field['isFirstField']
            for vbi in field['vbi']['vbiData']:
                if vbi & 0xf00000 == 0xf00000:
                    frame_bcd = vbi ^ 0xf00000
                    frame = 0
                    multiplier = 1
                    while frame_bcd > 0:
                        frame += (frame_bcd % 16) * multiplier
                        frame_bcd //= 16
                        multiplier *= 10
                    input_file_first_field += 2 * frame
                    break
            else:
                raise Exception('Invalid input file')
            f.seek(metadata['videoParameters']['fieldWidth'] * metadata['videoParameters'][
                'fieldHeight'] * 2 * (2 * args.start_frame - input_file_first_field))
        if args.frame_count is not None:
            data = f.read(metadata['videoParameters']['fieldWidth'] * metadata['videoParameters'][
                'fieldHeight'] * 4 * args.frame_count)
        else:
            data = f.read()

    data = numpy.ndarray((len(data) // (
            metadata['videoParameters']['fieldWidth'] * metadata['videoParameters'][
        'fieldHeight'] * 4), metadata['videoParameters']['fieldHeight'] * 2,
                          metadata['videoParameters']['fieldWidth']), dtype=numpy.uint16,
                         buffer=data)

    if data.shape[0] < 4:
        raise Exception('This script requires at least 4 frames to operate')

    if args.black_level is not None:
        black_level = args.black_level
    else:
        black_level = metadata['videoParameters']['black16bIre']
    if args.white_level is not None:
        white_level = args.white_level
    else:
        white_level = metadata['videoParameters']['white16bIre']

    inp = (data - black_level) / (white_level - black_level)

    if args.deghost is not None:
        inp = deghost(inp, *args.deghost)

    data = numpy.ndarray((4, inp.shape[1], inp.shape[2]))
    for i in range(4):
        data[i, :] = mean_with_outliers(inp[i::4])

    luma = numpy.mean(data, axis=0)

    chroma = deqam(data - luma)
    chroma = depal(chroma)
    chroma = numpy.mean(chroma, axis=0)

    luma = deinterlace(luma)
    chroma = deinterlace(chroma)
    chroma *= (3.0 / (14.0 * numpy.abs(numpy.mean(chroma[44:617, 109:129]))))

    fullcolor = numpy.ndarray((luma.shape[0], luma.shape[1], 3))
    fullcolor[:, :, 0] = luma
    fullcolor[:, :, 1] = (args.u_scale if args.u_scale is not None else 1.0) * numpy.real(chroma)
    fullcolor[:, :, 2] = (args.v_scale if args.v_scale is not None else 1.0) * numpy.imag(chroma)

    fullcolor = numpy.matvec(numpy.array(
        [[1.0, 0.0, 1.1402508551881414], [1.0, -0.3939307027516405, -0.5808092090310976],
         [1.0, 2.028397565922921, 0.0]]), fullcolor)

    output = fullcolor[44:620]
    output = numpy.pad(output, ((0, 0), (366, 365), (0, 0)), mode='edge')
    shift = 539.21902144097223
    if args.shift:
        shift += args.shift
    output = common.resample(output, shift=shift, axis=1)
    output = common.resample(output, 1554, axis=1)
    output = output[:, :788, :]
    outbuf = bytearray(numpy.prod(output.shape) * 2)
    outarr = numpy.ndarray(output.shape, dtype=numpy.uint16, buffer=outbuf)
    outarr[:] = numpy.round(
        numpy.minimum(numpy.maximum(output * (219.0 * 256.0) + 4096.0, 0.0), 65535.0))

    subprocess.run(
        ['magick', '-size', f'{output.shape[1]}x{numpy.prod(output.shape[0])}', '-depth', '16',
         'rgb:-', '+profile', 'icc', '-profile',
         os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'ITU-601-625-video16-v4.icc'), args.output_file], input=outbuf, check=True)


if __name__ == '__main__':
    sys.exit(_main(*sys.argv[1:]))
