#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys

import numpy

import common


def fix_arrow_tip(topbar):
    tip = topbar[1, 386:402, :]
    yuvtip = numpy.matvec(common.ColorSpace.BT601.from_rgb_matrix, tip)
    ytip = yuvtip[:, 0]
    scaled = (ytip - ytip[0]) / (1.0 - ytip[0])
    yuvtip = ((1.0 - scaled) * numpy.repeat(yuvtip[0, :].reshape((3, 1)), scaled.shape[0],
                                            axis=1) + scaled * numpy.repeat(
        numpy.array([[1.0], [0.0], [0.0]]), scaled.shape[0], axis=1)).swapaxes(0, 1)
    topbar[1, 386:402, :] = numpy.matvec(common.ColorSpace.BT601.to_rgb_matrix, yuvtip)


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Recreate the early widescreen version of Test Card F.')
    parser.add_argument('tcf_input', type=str,
                        help='File containing a cleanly restored version of the electronic Test Card F, sampled at 14.(769230) MHz (788x576). Will be passed through to ImageMagick.')
    parser.add_argument('tcfwide_input', type=str,
                        help='File containing a lower-quality version of the Widescreen Test Card F, sampled at 13.5 MHz (720x576), to pull the "BBC Widescreen" logo from.')
    parser.add_argument('output_file', type=str,
                        help='Output file. Will be passed through to ImageMagick.')
    args = parser.parse_args(args)

    resampler = common.resamplers.HybridResampler(mean_size=3,
                                                  backend_hi=common.resamplers.AliasedResampler())
    resample = lambda *args, **kwargs: common.resample(*args, **kwargs, resampler=resampler)

    data = subprocess.run(['magick', args.tcf_input, '-depth', '16', 'rgb:-'],
                          stdout=subprocess.PIPE, check=True).stdout
    assert len(data) == 788 * 576 * 3 * 2
    data = numpy.ndarray((576, 788, 3), dtype=numpy.uint16, buffer=data).copy()

    logodata = subprocess.run(['magick', args.tcfwide_input, '-depth', '16', 'rgb:-'],
                              stdout=subprocess.PIPE, check=True).stdout
    assert len(logodata) == 720 * 576 * 3 * 2
    logodata = numpy.ndarray((576, 720, 3), dtype=numpy.uint16, buffer=logodata)
    logodata = (logodata - 4096) / (219.0 * 256.0)

    # Remove the logos
    data[447:475, 383:407, :] = 32238
    data[496:527, 337:452, :] = 32238
    data = (data - 4096) / (219.0 * 256.0)
    fix_arrow_tip(data)

    # ==== Copy the good parts ====
    result = numpy.zeros((576, 1024, 3))
    result[30:, :224, :] = data[30:, 10:234, :]
    result[30:, 352:672, :] = data[30:, 234:554, :]
    result[30:, 800:, :] = data[30:, 554:778, :]
    result = result.swapaxes(0, 1)
    result[:12, :256] = result[12, :256]
    result[:12, -256:] = result[12, -256:]
    result[-12:, :256] = result[-12, :256]
    result[-12:, -256:] = result[-12, -256:]
    result = result.swapaxes(0, 1)

    # ==== Bottom castellations ====
    result[542:, 224:288, :] = result[542:, 160:224, :]
    result[542:, 288:352, :] = result[542:, 352:416, :]
    result[542:, 672:736, :] = result[542:, 608:672, :]
    result[542:, 736:800, :] = result[542:, 800:864, :]
    result[575] = result[574]
    for ch in range(result.shape[2]):
        result[575, 484:540, ch] = numpy.linspace(result[575, 483, ch], result[575, 540, ch], 58)[
            1:-1]

    # ==== Grid reconstruction ====
    result[:232, 224:232, :] = result[:232, 352:360, :]
    result[344:542, 224:232, :] = result[344:542, 352:360, :]
    result[280:296, 224:232, :] = 0.5 * (result[216:232, 224:232, :] + result[344:360, 224:232, :])
    for ch in range(result.shape[2]):
        for x in range(224, 232):
            result[232:280, x, ch] = numpy.linspace(result[231, x, ch], result[280, x, ch], 50)[
                1:-1]
            result[296:344, x, ch] = numpy.linspace(result[295, x, ch], result[344, x, ch], 50)[
                1:-1]

    result[:232, 344:352, :] = result[:232, 664:672, :]
    result[344:542, 344:352, :] = result[344:542, 664:672, :]
    result[280:296, 344:352, :] = 0.5 * (result[216:232, 344:352, :] + result[344:360, 344:352, :])
    for ch in range(result.shape[2]):
        for x in range(344, 352):
            result[232:280, x, ch] = numpy.linspace(result[231, x, ch], result[280, x, ch], 50)[
                1:-1]
            result[296:344, x, ch] = numpy.linspace(result[295, x, ch], result[344, x, ch], 50)[
                1:-1]

    result[:542, 280:288, :] = result[:542, 344:352, :]
    result[:542, 288:296, :] = result[:542, 224:232, :]
    for ch in range(result.shape[2]):
        for y in range(542):
            result[y, 232:280, ch] = numpy.linspace(result[y, 231, ch], result[y, 280, ch], 50)[
                1:-1]
            result[y, 296:344, ch] = numpy.linspace(result[y, 295, ch], result[y, 344, ch], 50)[
                1:-1]

    result[:542, 672:800, :] = result[:542, 224:352, :]

    # ==== Scale the top castellation independently ====
    topbar = data[0:30, 10:778]
    topbar[0] = topbar[1]
    for ch in range(result.shape[2]):
        topbar[0, 354:414, ch] = numpy.linspace(topbar[0, 353, ch], topbar[0, 414, ch], 62)[1:-1]
    topbar[29] = 2.0 * topbar[29] - 1.0
    orig_topbar = topbar
    topbar = resample(topbar, 1034, axis=1, pad_mode='symmetric')[:, 5:1029, :]
    topbar[:, 484:540, :] = orig_topbar[:, 356:412, :]
    topbar[:, :48, :] = 1.0
    topbar[:, -48:, :] = 1.0

    result[0:29] = topbar[0:29]
    result[29] = 0.5 * (result[30] + topbar[29])

    # ==== Fix the darkened grayscale block ====
    result[220:240, 162:225, :] = result[219, 162:225, :]

    # ==== Clear the frequency grating area
    result[164, 800:864, :] = result[411, 800:864, :]
    result[165:411, 800:864, :] = (result[411, 800:864, :] - result[411, 832, :]) / (
            1.0 - result[411, 832, :])

    # ==== Resample the result ====
    result = numpy.pad(result, ((0, 0), (1024, 1024), (0, 0)), 'reflect')
    result = resample(result, shift=551.0 / 702.0, axis=1, pad_mode='edge')
    result = result[:, 512:2560, :]
    result = resample(result, 2 * 702, axis=1)
    result = result[:, 342:1062, :]

    # ==== Frequency gratings ====
    result[164:412, 557:563, :] = result[164:412, 558:564, :]
    result = result.swapaxes(1, 2)
    for i, freq in enumerate(numpy.array([12, 20, 24, 28, 32, 36]) / 81.0):
        startline = 165 + i * 41
        endline = startline + 41
        if i == 0:
            startline -= 1
        elif i == 5:
            endline += 1
        line = numpy.cos(
            (numpy.linspace(-20.76 * freq, 21.24 * freq, 43) % 1.0) * 2.0 * numpy.pi) * 0.4 + 0.5
        result[startline:endline, :, 557:600] += (1.0 - result[
            startline:endline, :, 557:600]) * line
    result = result.swapaxes(1, 2)

    # ==== BBC Widescreen logo ====
    result[496:527, 237:482, :] = logodata[496:527, 237:482, :]

    outbuf = bytearray(numpy.prod(result.shape) * 2)
    output = numpy.ndarray(result.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:] = numpy.round(
        numpy.minimum(numpy.maximum(result * (219.0 * 256.0) + 4096.0, 0.0), 65535.0))
    subprocess.run(
        ['magick', '-size', f'{output.shape[1]}x{numpy.prod(output.shape[0])}', '-depth', '16',
         'rgb:-', '+profile', 'icc', '-profile',
         os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'ITU-601-625-video16-v4.icc'), '-define', 'png:color-type=2',
         args.output_file], input=outbuf, check=True)


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
