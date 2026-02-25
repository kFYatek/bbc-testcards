#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess

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


def _main():
    resampler = common.resamplers.HybridResampler(mean_size=3,
                                                  backend_hi=common.resamplers.AliasedResampler())
    resample = lambda *args, **kwargs: common.resample(*args, **kwargs, resampler=resampler)
    data = subprocess.run(['magick', '../TestCardFElec-788.png', '-depth', '16', 'rgb:-'],
                          stdout=subprocess.PIPE, check=True).stdout
    data = numpy.ndarray((576, 788, 3), dtype=numpy.uint16, buffer=data)
    data = (data - 4096) / (219.0 * 256.0)
    fix_arrow_tip(data)
    # Shift to make the samples symmetrical
    data = resample(data, shift=5.0 / 9.0, axis=1, pad_mode='edge')

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

    # ==== Scale the top castellation independently ====
    topbar = data[0:30, 10:778]
    topbar[0] = topbar[1]
    topbar[:, 354:414, :] = resample(
        resample(topbar[1:, 355:413, :], 30, axis=0, pad_mode='symmetric'), 60, axis=1,
        pad_mode='symmetric')
    topbar[29] = 2.0 * topbar[29] - 1.0
    orig_topbar = topbar
    topbar = resample(topbar, 1034, axis=1)[:, 5:1029, :]
    topbar[:, 484:540, :] = orig_topbar[:, 356:412, :]
    topbar[:, :48, :] = 1.0
    topbar[:, -48:, :] = 1.0

    result[0:29] = topbar[0:29]
    result[29] = 0.5 * (result[30] + topbar[29])

    # ==== Resample the result ====
    result = numpy.pad(result, ((0, 0), (1024, 1024), (0, 0)), 'reflect')
    result = resample(result, shift=161.0 / 702.0, axis=1, pad_mode='edge')
    result = result[:, 512:2560, :]
    result = resample(result, 2 * 702, axis=1)
    result = result[:, 342:1062, :]

    outbuf = bytearray(numpy.prod(result.shape) * 2)
    output = numpy.ndarray(result.shape, dtype=numpy.uint16, buffer=outbuf)
    output[:] = numpy.round(
        numpy.minimum(numpy.maximum(result * (219.0 * 256.0) + 4096.0, 0.0), 65535.0))
    subprocess.run(
        ['magick', '-size', f'{output.shape[1]}x{numpy.prod(output.shape[0])}', '-depth', '16',
         'rgb:-', '../TestCardFWide-new.png'], input=outbuf, check=True)


if __name__ == "__main__":
    _main()
