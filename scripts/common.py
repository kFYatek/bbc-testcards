# -*- coding: utf-8 -*-
import enum
import typing

import numpy
import scipy.fft
import scipy.signal


class ColorSpace(enum.Enum):
    YUV = 0
    GRAYSCALE = 1
    BT601 = 601
    BT709 = 709


ColorSpace.YUV.from_rgb_matrix = numpy.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
ColorSpace.YUV.to_rgb_matrix = numpy.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

ColorSpace.GRAYSCALE.from_rgb_matrix = numpy.array(
    [[0.299, 0.587, 0.114], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
ColorSpace.GRAYSCALE.to_rgb_matrix = numpy.array(
    [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

ColorSpace.BT601.from_rgb_matrix = numpy.array(
    [[0.299, 0.587, 0.114], [-0.16873589164785552, -0.3312641083521445, 0.5],
     [0.5, -0.4186875891583452, -0.08131241084165478]])
ColorSpace.BT601.to_rgb_matrix = numpy.array(
    [[1.0, 0.0, 1.402], [1.0, -0.34413628620102216, -0.7141362862010221], [1.0, 1.772, 0.0]])

ColorSpace.BT709.from_rgb_matrix = numpy.array(
    [[0.2126, 0.7152, 0.0722], [-0.11457210605733995, -0.3854278939426601, 0.5],
     [0.5, -0.4541529083058166, -0.04584709169418339]])
ColorSpace.BT709.to_rgb_matrix = numpy.array(
    [[1.0, 0.0, 1.5748], [1.0, -0.18732427293064877, -0.4681242729306488], [1.0, 1.8556, 0.0]])


class ScalingMode(enum.Enum):
    NONE = 0
    VERTICAL = 1
    CANONICAL = 2
    SQUARE_PIXELS = 3
    PAL_4FSC = 4


class ColorConversion(enum.Enum):
    NONE = 0
    AUTO = 1
    FORCE601 = 2
    FORCE601TO709 = 3
    LINEAR = 4


class OriginalResolution(enum.Enum):
    HD1080 = enum.auto()
    PAL169 = enum.auto()
    PAL43 = enum.auto()
    SYSA43 = enum.auto()
    SYSA54 = enum.auto()


class TestCardDefinition(typing.NamedTuple):
    name: str
    frame: int
    mode: OriginalResolution
    src_left: float = 0.0
    src_top: float = 0.0


class ScalingDimensions(typing.NamedTuple):
    precrop_w: int
    scale_w: int
    crop_w: int
    scale_h: int
    sample_rate_mhz: float


def get_scaling_dimensions(scaling_mode: ScalingMode, original_resolution: OriginalResolution) -> \
        typing.Optional[ScalingDimensions]:
    if scaling_mode is ScalingMode.NONE:
        return None
    elif original_resolution is OriginalResolution.HD1080:
        return ScalingDimensions(1920, 1920, 1920, 1080, 74.25)

    if scaling_mode is ScalingMode.VERTICAL:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(2560, 2560, 1970, 576, 36.92307692307692)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 1920, 1478, 576, 27.692307692307693)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1920, 1920, 1478, 378, 17.944615384615386)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1920, 1920, 1386, 378, 16.823076923076922)
    elif scaling_mode is ScalingMode.CANONICAL:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(2560, 936, 720, 576, 13.5)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 936, 720, 576, 13.5)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1920, 936, 720, 378, 8.748)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1400, 728, 720, 378, 8.748)
    elif scaling_mode is ScalingMode.SQUARE_PIXELS:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(1980, 1056, 1052, 576, 19.692307692307693)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 1024, 788, 576, 14.76923076923077)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1480, 518, 518, 378, 6.280615384615385)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1400, 490, 486, 378, 5.888076923076923)
    elif scaling_mode is ScalingMode.PAL_4FSC:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(12288, 5902, 946, 576, 17.734375)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(9216, 5902, 946, 576, 17.734375)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(9216, 5902, 946, 378, 11.491875)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(8640, 5902, 946, 378, 11.491875)


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


CARDS = [TestCardDefinition('Test Card X', 600, OriginalResolution.HD1080),
         TestCardDefinition('Television Eye', 1557, OriginalResolution.HD1080),
         TestCardDefinition('Tuning Signal', 2030, OriginalResolution.SYSA54, 0.27, -1.867),
         TestCardDefinition('Circle and line', 2505, OriginalResolution.HD1080),
         TestCardDefinition('Test Card A', 3009, OriginalResolution.SYSA43, 0, -1.5),
         TestCardDefinition('Test Card B', 3507, OriginalResolution.SYSA43, 1.54, -1),
         TestCardDefinition('Test Card C', 4007, OriginalResolution.SYSA43, 0, 0),
         TestCardDefinition('Test Card D', 4511, OriginalResolution.SYSA43, 0, 0.867),
         TestCardDefinition('Test Card F (optical)', 5011, OriginalResolution.PAL43, 0.55, -1),
         TestCardDefinition('Test Card F (electronic)', 5515, OriginalResolution.PAL43, -0.5, -1),
         TestCardDefinition('Test Card J', 6015, OriginalResolution.PAL43, 0, -1),
         TestCardDefinition('Test Card F widescreen', 6517, OriginalResolution.PAL169, 1.35, -1),
         TestCardDefinition('Test Card W', 7017, OriginalResolution.PAL169),
         TestCardDefinition('Test Card 3D', 7988, OriginalResolution.HD1080), ]
