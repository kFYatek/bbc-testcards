#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import PIL.Image
import numpy
import scipy.signal

import common

with open('/dev/stdin', 'rb') as f:
    data = f.read()

if len(data) == 12 * 1920 * 1080:
    width = 1920
    height = 1080
elif len(data) % (12 * 576) == 0 and len(data) // (12 * 576) >= 720:
    width = len(data) // (12 * 576)
    height = 576
elif len(data) % (12 * 378) == 0 and len(data) // (12 * 378) >= 486:
    width = len(data) // (12 * 378)
    height = 378

yuvdata_raw = numpy.ndarray((3, height, width), dtype='float32', buffer=bytearray(data))
yuvdata = numpy.zeros(yuvdata_raw.shape)
yuvdata[:, :, :] = yuvdata_raw

try:
    COLORSPACE = common.ColorSpace(int(os.environ.get('COLORSPACE')))
except Exception:
    COLORSPACE = common.ColorSpace.BT709
LIMITED = bool(int(os.environ.get('LIMITED') or '0'))

try:
    CARD = common.CARDS[int(os.environ['CARD'])]
except Exception:
    CARD = None

try:
    SCALE = common.ScalingMode(int(os.environ.get('SCALE')))
except Exception:
    SCALE = common.ScalingMode.NONE


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
        data = scipy.fft.irfft(fft, axis=-1)
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
    if dimensions is not None and height != dimensions.scale_h:
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

if COLORSPACE is common.ColorSpace.BT601:
    convmatrix = numpy.array(
        [[1.0, 0.0, 1.402], [1.0, -0.34413628620102216, -0.7141362862010221], [1.0, 1.772, 0.0]])
elif COLORSPACE is common.ColorSpace.BT709:
    convmatrix = numpy.array(
        [[1.0, 0.0, 1.5748], [1.0, -0.18732427293064877, -0.4681242729306488], [1.0, 1.8556, 0.0]])

rgbdata = numpy.matvec(convmatrix, yuvdata, axes=[(0, 1), (0), (2)])

if LIMITED:
    rgbdata *= 219.0
    rgbdata += 16.0
else:
    rgbdata *= 255.0

outbuf = bytearray(rgbdata.size)
output = numpy.ndarray(rgbdata.shape, dtype='uint8', buffer=outbuf)
output[:, :, :] = numpy.round(numpy.minimum(numpy.maximum(rgbdata, 0.0), 255.0))

im = PIL.Image.frombuffer('RGB', (output.shape[1], output.shape[0]), outbuf)
with open('/dev/stdout', 'wb') as f:
    im.save(f, format='PNG')
