#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os.path
import subprocess
import sys
import zipfile

import numpy

import common


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Recreate the BBC Test Card G variant of the Philips pattern.')
    parser.add_argument('output_file', type=str,
                        help='Output file. Will be passed through to ImageMagick.')
    args = parser.parse_args(args)

    with zipfile.ZipFile(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sources',
                         '8633vid_dat.zip')) as archive:
        fulldata = []
        for ch in (1, 2, 3):
            with archive.open(f'CHANNEL{ch}.DAT') as f:
                fulldata.append(f.read())

    fulldata_raw = numpy.stack(
        [numpy.ndarray((len(ch) // 2048, 1024), dtype=numpy.uint16, buffer=ch) for ch in fulldata],
        axis=-1)
    fulldata = numpy.zeros(fulldata_raw.shape)
    fulldata[..., 0] = (fulldata_raw[..., 0] - 64.0) / 876.0
    fulldata[..., 1:] = (fulldata_raw[..., 1:] - 512.0) / 896.0

    fulldata = fulldata[:, 16:736, :]

    yuvdata = fulldata[1382:1958, :, :]

    # Reconstruct shading around the frequency gratings and remove PLUGE
    yuvdata[308:350, 152:352, 0] = (219.0 * yuvdata[349, 152:352, 0] + 11.0) / (
            219.0 * yuvdata[350, 152:352, 0] + 11.0)
    yuvdata[308:350, 368:568, 0] = (219.0 * yuvdata[349, 368:568, 0] + 11.0) / (
            219.0 * yuvdata[350, 368:568, 0] + 11.0)
    yuvdata[350:392, 152:568, 0] = 1.0
    yuvdata[308:350, 352:368, :] = fulldata[6268:6310, 352:368, :]

    # Make clean backgroud grid
    griddata = yuvdata.copy()
    griddata[32:544, 149:572, :] = yuvdata[31, 149:572, :]
    griddata[162:414, 120:149, :] = yuvdata[161, 120:149, :]
    griddata[162:414, 572:600, :] = yuvdata[161, 572:600, :]
    griddata[56:560:42, 149:572, 0] = 1.0
    griddata[57:561:42, 149:572, 0] = 1.0
    griddata[182:434:42, 120:600, 0] = 1.0
    griddata[183:435:42, 120:600, 0] = 1.0

    # Extend the circle data so that it can be cropped differently again
    circledata = yuvdata.copy()
    circledata[32:56, 120:600, :] = [1.0, 0.0, 0.0]
    circledata[56:98, 120:280, :] = [1.0, 0.0, 0.0]
    circledata[56:98, 440:600, :] = [1.0, 0.0, 0.0]
    circledata[98:140, 120:240, :] = [0.0, 0.0, 0.0]
    circledata[98:140, 480:600, :] = [0.0, 0.0, 0.0]
    circledata[140:181, 120:600, :] = circledata[181, 120:600, :]
    circledata[140:182, 120:154, :] = [0.0, 0.0, 0.0]
    circledata[140:182, 560:600, :] = [0.75, 0.0, 0.0]
    circledata[182:268, 120:160, :] = circledata[182, 160, :]
    circledata[182:268, 560:600, :] = circledata[182, 560, :]
    circledata[268:308, 120:140, :] = circledata[268:308, 140:141, :]
    circledata[268:308, 580:600, :] = circledata[268:308, 579:580, :]
    circledata[308:392, 120:152, :] = [1.0, 0.0, 0.0]
    circledata[308:392, 568:600, :] = [1.0, 0.0, 0.0]
    circledata[392:434, 120:180, :] = [0.0, 0.0, 0.0]
    circledata[392:434, 540:600, :] = [1.0, 0.0, 0.0]
    circledata[434:476, 120:220, :] = [1.0, 0.0, 0.0]
    circledata[434:476, 480:600, :] = [1.0, 0.0, 0.0]
    circledata[477:544, 210:510, :] = circledata[476, 210:510, :]
    circledata[476:544, 120:210, :] = circledata[476, 210, :]
    circledata[476:544, 510:600, :] = circledata[476, 509, :]

    # Test Card G specific modifications
    circledata[224:268, 152:352, 0] = circledata[224, 152:352, 0] / circledata[223, 152:352, 0]
    circledata[224:268, 368:568, 0] = circledata[224, 368:568, 0] / circledata[223, 368:568, 0]
    circledata[224:268, 152:568, 1:] = 0.0
    circledata[224:268, 120:152, :] = [1.0, 0.0, 0.0]
    circledata[224:268, 568:600, :] = [1.0, 0.0, 0.0]
    circledata[140:224, 120:600, 0] += 0.25
    circledata[224:268, 120:352, :] = circledata[224:268, 120:352, 0:1] * circledata[
        223, 120:352, :]
    circledata[224:268, 368:600, :] = circledata[224:268, 368:600, 0:1] * circledata[
        223, 368:600, :]
    circledata[476:600, 120:600, 0] += 0.25

    # TODO: Remake frequency gratings
    # TODO: Anti-PAL

    # Old-style circle mask
    circlemask = numpy.zeros(griddata.shape[:2])
    for y in range(36, 540):
        delta = 252.0 ** 2.0 - (y - 287.5) ** 2.0
        if delta <= 0.0:
            continue
        xradius = numpy.sqrt(delta)
        # Simulate the limited precision of original PM5544
        xradius = numpy.floor(255.0 * xradius / 252.0 + 0.5)
        xradius *= 2457.0 / 2720.0
        # xradius = numpy.floor(xradius + 0.5)
        # xradius *= 702.0 / 768.0
        xl = 360.0 - xradius
        xr = 360.0 + xradius
        xll = int(numpy.ceil(xl - 1.25))
        xlr = int(numpy.floor(xl + 1.25))
        xrl = int(numpy.ceil(xr - 1.25))
        xrr = int(numpy.floor(xr + 1.25))
        for x in range(xll, xlr + 1):
            circlemask[y, x] = 0.5 - 0.5 * numpy.cos((x - xl + 1.25) * numpy.pi / 2.5)
        circlemask[y, xlr + 1:xrl] = 1.0
        for x in range(xrl, xrr + 1):
            circlemask[y, x] = 0.5 + 0.5 * numpy.cos((x - xr + 1.25) * numpy.pi / 2.5)

    outdata = (circlemask * circledata.transpose((2, 0, 1)) + (
            1.0 - circlemask) * griddata.transpose((2, 0, 1))).transpose((1, 2, 0))

    rgbdata = numpy.matvec(common.ColorSpace.BT601.to_rgb_matrix, outdata)

    outbuf = bytearray(numpy.prod(rgbdata.shape) * 2)
    output = numpy.ndarray(rgbdata.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:] = numpy.round(
        numpy.minimum(numpy.maximum(rgbdata * (219.0 * 256.0) + 4096.0, 0.0), 65535.0))
    subprocess.run(
        ['magick', '-size', f'{output.shape[1]}x{numpy.prod(output.shape[0])}', '-depth', '16',
         'rgb:-', '+profile', 'icc', '-profile',
         os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'icc',
                      'ITU-601-625-video16-v4.icc'), '-define', 'png:color-type=2',
         args.output_file], input=outbuf, check=True)


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
