# -*- coding: utf-8 -*-
import os
import sys

import scipy.interpolate
import vapoursynth

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

del sys.path[0]

clip = vapoursynth.core.bs.VideoSource(source='This Is BBC HD_20130326_0120.ts')

CARD = common.CARDS[int(os.environ['CARD'])]
CLAMP = bool(int(os.environ.get('CLAMP') or '0'))

try:
    SCALE = common.ScalingMode(int(os.environ.get('SCALE')))
except Exception:
    SCALE = common.ScalingMode.CANONICAL

try:
    COLORCONV = common.ColorConversion(int(os.environ.get('COLORCONV')))
except Exception:
    COLORCONV = common.ColorConversion.NONE

sys.stderr.write(f'Rendering {CARD.name}\n')
sys.stderr.write(f'Scaling mode: {SCALE}\n')
sys.stderr.write(f'Color conversion mode: {COLORCONV}\n')
sys.stderr.write(f'Clamping: {CLAMP}\n')

clip = clip[CARD.frame]

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

if SCALE is not common.ScalingMode.NONE:
    if CARD.mode is common.OriginalResolution.PAL169:
        rclip = vapoursynth.core.std.FlipHorizontal(clip)
        clip = vapoursynth.core.std.StackHorizontal([rclip, clip, rclip])
        clip = vapoursynth.core.std.CropAbs(clip, 2560, 1080, left=1600)
    precrop_w = None
    if CARD.mode in (common.OriginalResolution.PAL169, common.OriginalResolution.PAL43,
                     common.OriginalResolution.SYSA43):
        if SCALE is common.ScalingMode.CANONICAL:
            scale_w = 936
            crop_w = 720
        elif SCALE is common.ScalingMode.SQUARE_PIXELS:
            if CARD.mode is common.OriginalResolution.PAL169:
                precrop_w = 1980
                scale_w = 1056
                crop_w = 1052
            elif CARD.mode is common.OriginalResolution.PAL43:
                scale_w = 1024
                crop_w = 788
            else:
                precrop_w = 1480
                scale_w = 518
                crop_w = None
        elif CARD.mode is common.OriginalResolution.PAL169:
            scale_w = 2560
            crop_w = 1970
        else:
            scale_w = 1920
            crop_w = 1478
    elif CARD.mode is common.OriginalResolution.SYSA54:
        if SCALE is common.ScalingMode.VERTICAL:
            scale_w = 1920
            crop_w = 1386
        else:
            precrop_w = 1400
            if SCALE is common.ScalingMode.CANONICAL:
                scale_w = 728
                crop_w = 720
            elif SCALE is common.ScalingMode.SQUARE_PIXELS:
                scale_w = 490
                crop_w = 486
    if CARD.mode in (common.OriginalResolution.PAL169, common.OriginalResolution.PAL43):
        height = 576
    elif CARD.mode in (common.OriginalResolution.SYSA43, common.OriginalResolution.SYSA54):
        height = 378

    if CARD.mode is not common.OriginalResolution.HD1080:
        if precrop_w is not None:
            clip = vapoursynth.core.std.CropAbs(clip, precrop_w, 1080,
                                                left=(clip.width - precrop_w) // 2)
        clip = vapoursynth.core.descale.Delanczos(clip, scale_w, height,
                                                  src_left=CARD.src_left * scale_w / clip.width,
                                                  src_top=CARD.src_top * height / clip.height)
        if crop_w is not None:
            clip = vapoursynth.core.std.CropAbs(clip, crop_w, height, left=(scale_w - crop_w) // 2)

if COLORCONV is common.ColorConversion.FORCE601TO709:
    clip = vapoursynth.core.std.SetFrameProps(clip, _Matrix=vapoursynth.MATRIX_BT470_BG,
                                              _Transfer=vapoursynth.TRANSFER_BT601,
                                              _Primaries=vapoursynth.PRIMARIES_BT470_BG)
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT709,
                                         transfer=vapoursynth.TRANSFER_BT709,
                                         primaries=vapoursynth.PRIMARIES_BT709)
elif COLORCONV is common.ColorConversion.FORCE601 or (
        COLORCONV is common.ColorConversion.AUTO and CARD.mode is not common.OriginalResolution.HD1080):
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT470_BG,
                                         transfer=vapoursynth.TRANSFER_BT601,
                                         primaries=vapoursynth.PRIMARIES_BT470_BG)

# Output
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
clip.set_output()
