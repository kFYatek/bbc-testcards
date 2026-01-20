# -*- coding: utf-8 -*-
import os
import sys

import scipy.interpolate
import vapoursynth

clip = vapoursynth.core.bs.VideoSource(source='This Is BBC HD_20130326_0120.ts')

CARDS = {  #
    0: ('Test Card X', 600, 0, 0.0, 0.0),  #
    1: ('Television Eye', 1557, 0, 0.0, 0.0),  #
    2: ('Tuning Signal', 2030, 4, -0.27, 1.867),  #
    3: ('Circle and line', 2505, 0, 0.0, 0.0),  #
    4: ('Test Card A', 3009, 3, 0.0, 1.5),  #
    5: ('Test Card B', 3507, 3, -1.54, 1),  #
    6: ('Test Card C', 4007, 3, 0.0, -0.867),  #
    7: ('Test Card D', 4511, 3, 0.0, -0.867),  #
    8: ('Test Card F (optical)', 5011, 2, -0.55, 1.0),  #
    9: ('Test Card F (electronic)', 5515, 2, 0.5, 1.0),  #
    10: ('Test Card J', 6015, 2, 0.0, 1.0),  #
    11: ('Test Card F widescreen', 6517, 1, -1.35, 1.0),  #
    12: ('Test Card W', 7017, 1, 0.0, 0.0),  #
    13: ('Test Card 3D', 7988, 0, 0.0, 0.0),  #
}

CARD = int(os.environ['CARD'])
SCALE = int(os.environ.get('SCALE') or '2')
# 0: don't scale; 1: scale vertical only; 2: scale to canonical sample rate; 3: scale to square pixels
CLAMP = int(os.environ.get('CLAMP') or '0')
COLORCONV = int(os.environ.get('COLORCONV') or '0')
# 0: no conversion; 1: auto; 2: force Rec.601; 3: force Rec.601 -> Rec.709

sys.stderr.write(f'Rendering {CARDS[CARD][0]}\n')

clip = clip[CARDS[CARD][1]]

MODE = CARDS[CARD][2]  # 0: no scaling; 1: PAL 16:9; 2: PAL 4:3; 3: 405-line 4:3; 4 - 405-line 5:4
SRC_LEFT = CARDS[CARD][3]
SRC_TOP = CARDS[CARD][4]

if SCALE <= 0:
    SCALE_HORIZ = 0
    MODE = 0
else:
    SCALE_HORIZ = SCALE - 1

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
    if CLAMP > 0:
        result = min(max(result, 16.0), 235.0)
    else:
        result = min(max(result, 0.0), 255.0)
    return (result - 16) / 219.0


def correct_uv(x):
    result = x - 128
    if CLAMP > 0:
        result = min(max(result, -112.0), 112.0)
    else:
        result = min(max(result, -128.0), 127.0)
    return result / 224.0


yclip = vapoursynth.core.std.Lut(yclip, function=correct_y, floatout=True)
uclip = vapoursynth.core.std.Lut(uclip, function=correct_uv, floatout=True)
vclip = vapoursynth.core.std.Lut(vclip, function=correct_uv, floatout=True)

clip = vapoursynth.core.std.ShufflePlanes([yclip, uclip, vclip], planes=[0, 0, 0],
                                          colorfamily=vapoursynth.YUV, prop_src=clip)

if MODE == 1:
    rclip = vapoursynth.core.std.FlipHorizontal(clip)
    clip = vapoursynth.core.std.StackHorizontal([rclip, clip, rclip])
    clip = vapoursynth.core.std.CropAbs(clip, 2560, 1080, left=1600)
precrop_w = None
if MODE == 1 or MODE == 2 or MODE == 3:
    if SCALE_HORIZ == 1:
        scale_w = 936
        crop_w = 720
    elif SCALE_HORIZ == 2:
        if MODE == 1:
            precrop_w = 1980
            scale_w = 1056
            crop_w = 1052
        elif MODE == 2:
            scale_w = 1024
            crop_w = 788
        else:
            precrop_w = 1480
            scale_w = 518
            crop_w = None
    elif MODE == 1:
        scale_w = 2560
        crop_w = 1970
    else:
        scale_w = 1920
        crop_w = 1478
elif MODE == 4:
    if SCALE_HORIZ == 0:
        scale_w = 1920
        crop_w = 1386
    else:
        precrop_w = 1400
        if SCALE_HORIZ == 1:
            scale_w = 728
            crop_w = 720
        elif SCALE_HORIZ == 2:
            scale_w = 490
            crop_w = 486
if MODE == 1 or MODE == 2:
    height = 576
elif MODE == 3 or MODE == 4:
    height = 378

if MODE != 0:
    if precrop_w is not None:
        clip = vapoursynth.core.std.CropAbs(clip, precrop_w, 1080,
                                            left=(clip.width - precrop_w) // 2)
    clip = vapoursynth.core.descale.Delanczos(clip, scale_w, height,
                                              src_left=SRC_LEFT * scale_w / clip.width,
                                              src_top=SRC_TOP * height / clip.height)
    if crop_w is not None:
        clip = vapoursynth.core.std.CropAbs(clip, crop_w, height, left=(scale_w - crop_w) // 2)

if COLORCONV >= 3:
    clip = vapoursynth.core.std.SetFrameProps(clip, _Matrix=vapoursynth.MATRIX_BT470_BG,
                                              _Transfer=vapoursynth.TRANSFER_BT601,
                                              _Primaries=vapoursynth.PRIMARIES_BT470_BG)
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT709,
                                         transfer=vapoursynth.TRANSFER_BT709,
                                         primaries=vapoursynth.PRIMARIES_BT709)
elif COLORCONV >= 2 or (COLORCONV >= 1 and MODE != 0):
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT470_BG,
                                         transfer=vapoursynth.TRANSFER_BT601,
                                         primaries=vapoursynth.PRIMARIES_BT470_BG)

# Output
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
clip.set_output()
