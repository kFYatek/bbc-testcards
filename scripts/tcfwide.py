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
    data = numpy.ndarray((576, 788, 3), dtype=numpy.uint16, buffer=data).copy()
    # Remove the logos
    data[447:475, 383:407, :] = 32238
    data[496:527, 337:452, :] = 32238
    data = (data - 4096) / (219.0 * 256.0)
    fix_arrow_tip(data)
    # Shift to make the samples symmetrical
    data = resample(data, shift=5.0 / 9.0, axis=1, pad_mode='edge')

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
    topbar = resample(topbar, 1034, shift_to_center=True, axis=1, pad_mode='symmetric')[
        :, 5:1029, :]
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
