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

SCALER = os.environ.get('SCALER') or 'Debilinear'

SCALER_H = os.environ.get('SCALER_H') or SCALER
SCALER_H = SCALER_H[0].upper() + SCALER_H[1:].lower()

SCALER_V = os.environ.get('SCALER_V') or SCALER
SCALER_V = SCALER_V[0].upper() + SCALER_V[1:].lower()

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

dimensions = common.get_scaling_dimensions(SCALE, CARD.mode)

if dimensions is not None:
    src_left = CARD.src_left
    src_top = CARD.src_top
    src_width = dimensions.precrop_w
    src_height = clip.height
    if SCALER_H[0:2] == 'De':
        scaler_h = getattr(vapoursynth.core.descale, SCALER_H)
        if dimensions.scale_w == dimensions.precrop_w:
            src_left = 0
        else:
            src_left *= -dimensions.scale_w / dimensions.precrop_w
        src_width = None
    else:
        scaler_h = getattr(vapoursynth.core.resize, SCALER_H)
    if SCALER_V[0:2] == 'De':
        scaler_v = getattr(vapoursynth.core.descale, SCALER_V)
        if dimensions.scale_h == clip.height:
            src_top = 0
        else:
            src_top *= -dimensions.scale_h / clip.height
        src_height = None
    else:
        scaler_v = getattr(vapoursynth.core.resize, SCALER_V)

    while dimensions.precrop_w > clip.width:
        rclip = vapoursynth.core.std.FlipHorizontal(clip)
        clip = vapoursynth.core.std.StackHorizontal([rclip, clip, rclip])
    if dimensions.precrop_w != clip.width:
        clip = vapoursynth.core.std.CropAbs(clip, dimensions.precrop_w, clip.height,
                                            left=(clip.width - dimensions.precrop_w) // 2)
    if SCALER_H == SCALER_V:
        clip = scaler_v(clip, dimensions.scale_w, dimensions.scale_h, src_left=src_left,
                        src_top=src_top, src_width=src_width, src_height=src_height)
    else:
        clip = scaler_h(clip, dimensions.scale_w, clip.height, src_left=src_left,
                        src_width=src_width)
        clip = scaler_v(clip, clip.width, dimensions.scale_h, src_top=src_top,
                        src_height=src_height)
    if dimensions.crop_w is not None:
        clip = vapoursynth.core.std.CropAbs(clip, dimensions.crop_w, clip.height,
                                            left=(clip.width - dimensions.crop_w) // 2)

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
