# -*- coding: utf-8 -*-
import enum
import os
import sys
import typing

import scipy.interpolate
import vapoursynth

clip = vapoursynth.core.bs.VideoSource(source='This Is BBC HD_20130326_0120.ts')


class ScalingMode(enum.Enum):
    NONE = 0
    VERTICAL = 1
    CANONICAL = 2
    SQUARE_PIXELS = 3


class ColorConversion(enum.Enum):
    NONE = 0
    AUTO = 1
    FORCE601 = 2
    FORCE601TO709 = 3


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


CARDS = [TestCardDefinition('Test Card X', 600, OriginalResolution.HD1080),
         TestCardDefinition('Television Eye', 1557, OriginalResolution.HD1080),
         TestCardDefinition('Tuning Signal', 2030, OriginalResolution.SYSA54, -0.27, 1.867),
         TestCardDefinition('Circle and line', 2505, OriginalResolution.HD1080),
         TestCardDefinition('Test Card A', 3009, OriginalResolution.SYSA43, 0.0, 1.5),
         TestCardDefinition('Test Card B', 3507, OriginalResolution.SYSA43, -1.54, 1),
         TestCardDefinition('Test Card C', 4007, OriginalResolution.SYSA43, 0.0, -0.867),
         TestCardDefinition('Test Card D', 4511, OriginalResolution.SYSA43, 0.0, -0.867),
         TestCardDefinition('Test Card F (optical)', 5011, OriginalResolution.PAL43, -0.55, 1.0),
         TestCardDefinition('Test Card F (electronic)', 5515, OriginalResolution.PAL43, 0.5, 1.0),
         TestCardDefinition('Test Card J', 6015, OriginalResolution.PAL169, 0.0, 1.0),
         TestCardDefinition('Test Card F widescreen', 6517, OriginalResolution.PAL169, -1.35, 1.0),
         TestCardDefinition('Test Card W', 7017, OriginalResolution.PAL169),
         TestCardDefinition('Test Card 3D', 7988, OriginalResolution.HD1080), ]

CARD = int(os.environ['CARD'])
CLAMP = bool(int(os.environ.get('CLAMP') or '0'))

try:
    SCALE = ScalingMode(int(os.environ.get('SCALE')))
except Exception:
    SCALE = ScalingMode.CANONICAL

try:
    COLORCONV = ColorConversion(int(os.environ.get('COLORCONV')))
except Exception:
    COLORCONV = ColorConversion.NONE

sys.stderr.write(f'Rendering {CARDS[CARD].name}\n')

clip = clip[CARDS[CARD].frame]

MODE = CARDS[CARD].mode
SRC_LEFT = CARDS[CARD].src_left
SRC_TOP = CARDS[CARD].src_top

if SCALE is ScalingMode.NONE:
    MODE = OriginalResolution.HD1080

# Nonlinearity precorrection
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444P8)
yclip, uclip, vclip = clip.std.SplitPlanes()

y_spline = scipy.interpolate.CubicSpline(
    [-16, 0, 16, 59, 88, 97, 100, 125, 149, 188, 196, 230, 235, 240, 245, 250, 255],
    [-16, 0, 16, 60, 90, 101, 104, 126, 147, 183, 191, 224, 235, 255, 275, 295, 315],
    bc_type='clamped')


def correct_y(x):
    # result = x
    result = float(y_spline(x))
    if CLAMP:
        result = min(max(result, 16.0), 235.0)
    else:
        result = min(max(result, 0.0), 255.0)
    return (result - 16) / 219.0


def correct_uv(x):
    result = x - 128
    if CLAMP:
        result = min(max(result, -112.0), 112.0)
    else:
        result = min(max(result, -128.0), 127.0)
    return result / 224.0


yclip = vapoursynth.core.std.Lut(yclip, function=correct_y, floatout=True)
uclip = vapoursynth.core.std.Lut(uclip, function=correct_uv, floatout=True)
vclip = vapoursynth.core.std.Lut(vclip, function=correct_uv, floatout=True)

clip = vapoursynth.core.std.ShufflePlanes([yclip, uclip, vclip], planes=[0, 0, 0],
                                          colorfamily=vapoursynth.YUV, prop_src=clip)

if MODE is OriginalResolution.PAL169:
    rclip = vapoursynth.core.std.FlipHorizontal(clip)
    clip = vapoursynth.core.std.StackHorizontal([rclip, clip, rclip])
    clip = vapoursynth.core.std.CropAbs(clip, 2560, 1080, left=1600)
precrop_w = None
if MODE in (OriginalResolution.PAL169, OriginalResolution.PAL43, OriginalResolution.SYSA43):
    if SCALE is ScalingMode.CANONICAL:
        scale_w = 936
        crop_w = 720
    elif SCALE is ScalingMode.SQUARE_PIXELS:
        if MODE is OriginalResolution.PAL169:
            precrop_w = 1980
            scale_w = 1056
            crop_w = 1052
        elif MODE is OriginalResolution.PAL43:
            scale_w = 1024
            crop_w = 788
        else:
            precrop_w = 1480
            scale_w = 518
            crop_w = None
    elif MODE is OriginalResolution.PAL169:
        scale_w = 2560
        crop_w = 1970
    else:
        scale_w = 1920
        crop_w = 1478
elif MODE is OriginalResolution.SYSA54:
    if SCALE is ScalingMode.VERTICAL:
        scale_w = 1920
        crop_w = 1386
    else:
        precrop_w = 1400
        if SCALE is ScalingMode.CANONICAL:
            scale_w = 728
            crop_w = 720
        elif SCALE is ScalingMode.SQUARE_PIXELS:
            scale_w = 490
            crop_w = 486
if MODE in (OriginalResolution.PAL169, OriginalResolution.PAL43):
    height = 576
elif MODE in (OriginalResolution.SYSA43, OriginalResolution.SYSA54):
    height = 378

if MODE is not OriginalResolution.HD1080:
    if precrop_w is not None:
        clip = vapoursynth.core.std.CropAbs(clip, precrop_w, 1080,
                                            left=(clip.width - precrop_w) // 2)
    clip = vapoursynth.core.descale.Delanczos(clip, scale_w, height,
                                              src_left=SRC_LEFT * scale_w / clip.width,
                                              src_top=SRC_TOP * height / clip.height)
    if crop_w is not None:
        clip = vapoursynth.core.std.CropAbs(clip, crop_w, height, left=(scale_w - crop_w) // 2)

if COLORCONV is ColorConversion.FORCE601TO709:
    clip = vapoursynth.core.std.SetFrameProps(clip, _Matrix=vapoursynth.MATRIX_BT470_BG,
                                              _Transfer=vapoursynth.TRANSFER_BT601,
                                              _Primaries=vapoursynth.PRIMARIES_BT470_BG)
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT709,
                                         transfer=vapoursynth.TRANSFER_BT709,
                                         primaries=vapoursynth.PRIMARIES_BT709)
elif COLORCONV is ColorConversion.FORCE601 or (
        COLORCONV is ColorConversion.AUTO and MODE is not OriginalResolution.HD1080):
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT470_BG,
                                         transfer=vapoursynth.TRANSFER_BT601,
                                         primaries=vapoursynth.PRIMARIES_BT470_BG)

# Output
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
clip.set_output()
