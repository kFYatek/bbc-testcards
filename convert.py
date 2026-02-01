#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import PIL.Image
import numpy
import scipy.signal

import common

try:
    COLORSPACE = common.ColorSpace(int(os.environ.get('COLORSPACE')))
except Exception:
    COLORSPACE = common.ColorSpace.BT601
LIMITED = bool(int(os.environ.get('LIMITED') or '0'))
RAW16IN = bool(int(os.environ.get('RAW16IN') or '0'))
RAW16OUT = bool(int(os.environ.get('RAW16OUT') or '0'))
FILEIN = os.environ.get('FILEIN')
PLOT = int(os.environ.get('PLOT') or '0')
PLOTSCALE = float(os.environ.get('PLOTSCALE') or '1')

try:
    CARD = common.CARDS[int(os.environ['CARD'])]
except Exception:
    CARD = None

try:
    SCALE = common.ScalingMode(int(os.environ.get('SCALE')))
except Exception:
    SCALE = common.ScalingMode.NONE

if FILEIN is not None:
    image = PIL.Image.open(FILEIN)
    width = image.width
    height = image.height
    rgbdata = numpy.array(image.get_flattened_data())
    rgbdata = rgbdata.reshape((height, width, 3))
    rgbdata = (rgbdata - 16.0) / 219.0
    rgbdata = rgbdata.transpose((2, 0, 1))

    if COLORSPACE is common.ColorSpace.BT601:
        convmatrix = numpy.array(
            [[0.299, 0.587, 0.114], [-0.16873589164785552, -0.3312641083521445, 0.5],
             [0.5, -0.4186875891583452, -0.08131241084165478]])
    elif COLORSPACE is common.ColorSpace.BT709:
        convmatrix = numpy.array(
            [[0.2126, 0.7152, 0.0722], [-0.11457210605733995, -0.3854278939426601, 0.5],
             [0.5, -0.4541529083058166, -0.04584709169418339]])
    else:
        convmatrix = None

    if convmatrix is not None:
        yuvdata = numpy.matvec(convmatrix, rgbdata, axes=[(0, 1), (0), (0)])
    else:
        yuvdata = rgbdata
else:
    with open('/dev/stdin', 'rb') as f:
        data = f.read()

    multiplier = 6 if RAW16IN else 12
    if len(data) == multiplier * 1920 * 1080:
        width = 1920
        height = 1080
    elif len(data) % (multiplier * 576) == 0 and len(data) // (multiplier * 576) >= 720:
        width = len(data) // (multiplier * 576)
        height = 576
    elif len(data) % (multiplier * 378) == 0 and len(data) // (multiplier * 378) >= 486:
        width = len(data) // (multiplier * 378)
        height = 378

    if RAW16IN:
        yuvdata_raw = numpy.ndarray((height, width, 3), dtype=numpy.uint16, buffer=bytearray(data))
    else:
        yuvdata_raw = numpy.ndarray((3, height, width), dtype=numpy.float32, buffer=bytearray(data))
    yuvdata = numpy.zeros(yuvdata_raw.shape)
    yuvdata[:, :, :] = yuvdata_raw

    if RAW16IN:
        yuvdata = numpy.transpose(yuvdata, (2, 0, 1))
        yuvdata /= 256.0
        yuvdata[0] -= 16.0
        yuvdata[0] /= 219.0
        yuvdata[1:] -= 128.0
        yuvdata[1:] /= 224.0


def apply_shift(data: numpy.array, shift: float, axis: int = -1):
    if axis < 0:
        axis = len(data.shape) + axis
    intshift = int(shift)
    if intshift != 0:
        data = numpy.roll(data, -intshift, axis=axis)
        data = numpy.swapaxes(data, 0, axis)
        if intshift > 0:
            data[-intshift:] = data[-intshift - 1]
        else:
            data[0:-intshift] = data[-intshift]
        data = numpy.swapaxes(data, 0, axis)
    shift = shift - intshift
    if shift != 0:
        data = numpy.swapaxes(data, len(data.shape) - 1, axis)
        data = numpy.pad(data, [(0, 0)] * (len(data.shape) - 1) + [(1, 1)], mode='edge')
        fft = scipy.fft.rfft(data, axis=-1)
        fft *= numpy.exp(
            numpy.array(range(fft.shape[-1])) * (2.0j * shift * numpy.pi / data.shape[-1]))
        data = scipy.fft.irfft(fft, n=data.shape[-1], axis=-1)
        data = numpy.delete(data, [0, -1], axis=-1)
        data = numpy.swapaxes(data, len(data.shape) - 1, axis)
    return data


def resample_with_mirrors(data: numpy.array, new_size: int, axis: int = -1):
    if axis < 0:
        axis = len(data.shape) + axis
    if new_size != data.shape[axis]:
        data = numpy.swapaxes(data, 0, axis)
        reversed = numpy.flip(data, axis=0)
        data = numpy.concatenate([reversed, data, reversed], axis=0)
        data = scipy.signal.resample(data, 3 * new_size, axis=0)
        data = data[new_size:2 * new_size]
        data = numpy.swapaxes(data, 0, axis)
    return data


dimensions = None
src_left = 0.0
src_top = 0.0
if CARD is not None:
    dimensions = common.get_scaling_dimensions(SCALE, CARD.mode)
    if width >= common.get_scaling_dimensions(common.ScalingMode.VERTICAL, CARD.mode).crop_w:
        src_left = CARD.src_left
    if height == 1080:
        src_top = CARD.src_top

if dimensions is not None:
    while dimensions.precrop_w > yuvdata.shape[2]:
        reversed = numpy.flip(yuvdata, axis=2)
        yuvdata = numpy.concatenate([reversed, yuvdata, reversed], axis=2)
    if dimensions.precrop_w != yuvdata.shape[2]:
        yuvdata = yuvdata[:, :, (yuvdata.shape[2] - dimensions.precrop_w) // 2:]
        yuvdata = yuvdata[:, :, :dimensions.precrop_w]
    src_left += yuvdata.shape[2] / (2 * dimensions.scale_w) - 0.5
    src_top += yuvdata.shape[1] / (2 * dimensions.scale_h) - 0.5

yuvdata = apply_shift(yuvdata, src_left, axis=2)
yuvdata = apply_shift(yuvdata, src_top, axis=1)

if dimensions is not None:
    yuvdata = resample_with_mirrors(yuvdata, dimensions.scale_w, axis=2)
    yuvdata = resample_with_mirrors(yuvdata, dimensions.scale_h, axis=1)
    if dimensions.crop_w != dimensions.scale_w:
        yuvdata = yuvdata[:, :, (yuvdata.shape[2] - dimensions.crop_w) // 2:]
        yuvdata = yuvdata[:, :, :dimensions.crop_w]

if FILEIN is None and COLORSPACE is common.ColorSpace.BT601:
    convmatrix = numpy.array(
        [[1.0, 0.0, 1.402], [1.0, -0.34413628620102216, -0.7141362862010221], [1.0, 1.772, 0.0]])
elif FILEIN is None and COLORSPACE is common.ColorSpace.BT709:
    convmatrix = numpy.array(
        [[1.0, 0.0, 1.5748], [1.0, -0.18732427293064877, -0.4681242729306488], [1.0, 1.8556, 0.0]])
else:
    convmatrix = None

if convmatrix is not None:
    outdata = numpy.matvec(convmatrix, yuvdata, axes=[(0, 1), (0), (0)])
else:
    outdata = yuvdata

if PLOT > 0:
    import matplotlib.pyplot
    import matplotlib.widgets

    UPSAMPLE = 32
    outdata = resample_with_mirrors(outdata, outdata.shape[2] * UPSAMPLE, axis=2)
    xdata = numpy.array(range(outdata.shape[2])) / UPSAMPLE

    fig = matplotlib.pyplot.figure()
    subplot = fig.add_subplot()
    subplot.set_autoscalex_on(True)
    subplot.set_autoscaley_on(False)
    if PLOT == 1 or convmatrix is not None or (
            FILEIN is not None and COLORSPACE is common.ColorSpace.YUV):
        subplot.set_ybound(-0.1 * PLOTSCALE, 1.1 * PLOTSCALE)
    else:
        subplot.set_ybound(-0.6 * PLOTSCALE, 0.6 * PLOTSCALE)
    matplotlib.pyplot.subplots_adjust(bottom=0.25)

    lineno = 0
    mpline, = subplot.plot(xdata, outdata[PLOT - 1, lineno] * PLOTSCALE)

    slider_frame = matplotlib.pyplot.axes([0.1, 0.1, 0.8, 0.03])
    slider = matplotlib.widgets.Slider(slider_frame, 'Line', 0, outdata.shape[1] - 1, valinit=0,
                                       valfmt='%d')


    def slider_update(val):
        lineno = int(numpy.floor(slider.val))
        mpline.set_ydata(outdata[PLOT - 1, lineno] * PLOTSCALE)
        subplot.set_title(f'Line {lineno}')
        subplot.relim()
        matplotlib.pyplot.draw()


    slider.on_changed(slider_update)
    slider_update(0)
    matplotlib.pyplot.show()
else:
    if LIMITED or RAW16OUT:
        if FILEIN is not None or convmatrix is not None:
            outdata *= 219.0
            outdata += 16.0
        else:
            outdata[0] *= 219.0
            outdata[0] += 16.0
            outdata[1:] *= 224.0
            outdata[1:] += 128.0
        if RAW16OUT:
            outdata *= 256.0
    else:
        if FILEIN is None and convmatrix is None:
            outdata[1:] += 0.5
        outdata *= 255.0

    outdata = numpy.transpose(outdata, (1, 2, 0))
    outbuf = bytearray(outdata.size * (2 if RAW16OUT else 1))
    output = numpy.ndarray(outdata.shape, dtype='uint16' if RAW16OUT else 'uint8', buffer=outbuf)
    output[:, :, :] = numpy.round(
        numpy.minimum(numpy.maximum(outdata, 0.0), 65535.0 if RAW16OUT else 255.0))

    with open('/dev/stdout', 'wb') as f:
        if RAW16OUT:
            f.write(outbuf)
        else:
            PIL.Image.frombuffer('RGB', (output.shape[1], output.shape[0]), outbuf).save(f,
                                                                                         format='PNG')
