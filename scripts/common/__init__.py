# -*- coding: utf-8 -*-
import enum
import typing
import warnings

import PIL.Image
import numpy

from . import resamplers

if not 'get_flattened_data' in PIL.Image.Image.__dict__.keys():
    PIL.Image.Image.get_flattened_data = PIL.Image.Image.getdata


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
    FSC_TIMES_4 = 4


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
    NTSC169 = enum.auto()
    NTSC43 = enum.auto()


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
        elif original_resolution is OriginalResolution.NTSC169:
            return ScalingDimensions(2560, 2560, 1938, 486, 36.32541517763296)
        elif original_resolution is OriginalResolution.NTSC43:
            return ScalingDimensions(1920, 1920, 1454, 486, 27.24406138322472)
    elif scaling_mode is ScalingMode.CANONICAL:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(2560, 936, 720, 576, 13.5)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 936, 720, 576, 13.5)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1920, 936, 720, 378, 8.748)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1400, 728, 720, 378, 8.748)
        elif original_resolution is OriginalResolution.NTSC169:
            return ScalingDimensions(25600, 9514, 720, 486, 13.5)
        elif original_resolution is OriginalResolution.NTSC43:
            return ScalingDimensions(19200, 9514, 720, 486, 13.5)
    elif scaling_mode is ScalingMode.SQUARE_PIXELS:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(1980, 1056, 1052, 576, 19.692307692307693)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 1024, 788, 576, 14.76923076923077)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1480, 518, 518, 378, 6.280615384615385)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1400, 490, 486, 378, 5.888076923076923)
        elif original_resolution is OriginalResolution.NTSC169:
            return ScalingDimensions(1960, 882, 872, 486, 16.346436829934834)
        elif original_resolution is OriginalResolution.NTSC43:
            return ScalingDimensions(1480, 666, 654, 486, 12.259827622451125)
    elif scaling_mode is ScalingMode.FSC_TIMES_4:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(12288, 5902, 946, 576, 17.734375)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(9216, 5902, 946, 576, 17.734375)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(9216, 5902, 946, 378, 11.491875)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(8640, 5902, 946, 378, 11.491875)
        elif original_resolution is OriginalResolution.NTSC169:
            return ScalingDimensions(2816, 1110, 764, 486, 14.318181818181818)
        elif original_resolution is OriginalResolution.NTSC43:
            return ScalingDimensions(2112, 1110, 764, 486, 14.318181818181818)


def resample(x: numpy.ndarray, num: int = None, shift: float = 0.0, shift_to_center: bool = False,
             axis: int = 0, resampler=resamplers.fft_resampler, pad_mode=None,
             **kwargs) -> numpy.ndarray:
    if axis < 0:
        axis = len(x.shape) + axis
    if num is None:
        num = x.shape[axis]
    if shift_to_center:
        shift += 0.5 - num / (2.0 * x.shape[axis])
    if num != x.shape[axis] or shift != 0.0:
        if pad_mode is not None:
            x = numpy.swapaxes(x, axis, len(x.shape) - 1)
            if pad_mode == 'reflect':
                pad_width = max(x.shape[-1] - 2, 0)
                newsize_float = num * (x.shape[-1] + pad_width) / x.shape[-1]
                newsize = int(round(newsize_float))
                if newsize != newsize_float:
                    warnings.warn('resampling with reflect padding and non-divisible sizes')
            else:
                pad_width = x.shape[-1]
                newsize = 2 * num
            if pad_mode == 'edge':
                pad_l = pad_width // 2
                pad_r = pad_width - pad_l
            else:
                pad_l = 0
                pad_r = pad_width
            x = numpy.pad(x, [(0, 0)] * (len(x.shape) - 1) + [(pad_l, pad_r)], mode=pad_mode,
                          **kwargs)
            if pad_l > 0:
                x = numpy.roll(x, -pad_l, axis=-1)
            x = resample(x=x, num=newsize, shift=shift, shift_to_center=False, axis=-1,
                         resampler=resampler, pad_mode=None)
            x = x[..., :num]
            x = numpy.swapaxes(x, axis, len(x.shape) - 1)
        else:
            if kwargs:
                raise Exception('kwargs are not allowed when pad_mode is None')
            x = resampler(x, num, shift, axis)
    return x


def read_image(filename: str, infer_dimensions=None) -> tuple[numpy.ndarray, int]:
    if filename.startswith('raw16:') or filename.startswith('rawfloat:'):
        format, args = filename.split(':', 1)
        if format == 'raw16':
            dtype = numpy.uint16
            range = 65535
            bytes = 6
        else:
            dtype = numpy.float32
            range = 1
            bytes = 12
        if '@' in args:
            filename, args = args.split('@', 1)
        else:
            filename = '/dev/stdin'
        with open(filename, 'rb') as f:
            rawdata = f.read()
        if 'x' in args:
            width, height = (int(val) for val in args.split('x'))
        else:
            if infer_dimensions is None:
                raise Exception('Cannot read image, unknown dimensions')
            assert len(rawdata) % bytes == 0
            width, height = infer_dimensions(len(rawdata) // bytes)
        if dtype == numpy.float32:
            data = numpy.ndarray((3, height, width), dtype=numpy.float32, buffer=rawdata).transpose(
                (1, 2, 0))
        else:
            data = numpy.ndarray((height, width, 3), dtype=dtype, buffer=rawdata)
    else:
        im = PIL.Image.open(filename)
        if im.mode == 'P':
            im = im.convert(im.palette.mode)

        data = numpy.array(im.get_flattened_data())
        data = data.reshape((im.height, im.width, len(im.getbands())))
        if ';16' in im.mode:
            range = 65535
        else:
            range = 255
    return data, range


def load_and_process_image(file: str, colorspace: ColorSpace = None) -> numpy.ndarray:
    def infer_dimensions(samples):
        if samples % 1080 == 0 and samples // 1080 >= 1440:
            return samples // 1080, 1080
        elif samples % 576 == 0 and samples // 576 >= 720:
            return samples // 576, 576
        elif samples % 486 == 0 and samples // 486 >= 654:
            return samples // 486, 486
        elif samples % 480 == 0 and samples // 480 >= 654:
            return samples // 480, 480
        elif samples % 378 == 0 and samples // 378 >= 486:
            return samples // 378, 378
        raise Exception('Unable to infer image dimensions')

    data, data_range = read_image(file, infer_dimensions)
    if colorspace is None:
        if ':' in file and file.startswith('raw'):
            colorspace = ColorSpace.YUV
        else:
            colorspace = ColorSpace.BT601

    if colorspace is ColorSpace.YUV:
        yuvdata = 1.0 * data
        if data_range in (255, 65535):
            if data_range == 65535:
                yuvdata /= 256.0
            yuvdata[0] -= 16.0
            yuvdata[0] /= 219.0
            yuvdata[1:] -= 128.0
            yuvdata[1:] /= 224.0
        else:
            assert data_range == 1
    else:
        if data.shape[2] == 1:
            data = data.repeat(3, axis=2)
        if data_range == 65535:
            data = (data - 4096.0) / 56064.0
        elif data_range == 255:
            data = (data - 16.0) / 219.0
        else:
            assert data_range == 1
        yuvdata = numpy.matvec(colorspace.from_rgb_matrix, data, axes=[(0, 1), 2, 2])
    return yuvdata


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
