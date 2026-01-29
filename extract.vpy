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
EQUALIZE = bool(int(os.environ.get('EQUALIZE') or '1'))
ANTIRING = float(os.environ.get('ANTIRING') or '0')

try:
    SCALE = common.ScalingMode(int(os.environ.get('SCALE')))
except Exception:
    SCALE = common.ScalingMode.CANONICAL

try:
    COLORCONV = common.ColorConversion(int(os.environ.get('COLORCONV')))
except Exception:
    COLORCONV = common.ColorConversion.AUTO

SCALER = os.environ.get('SCALER') or 'Debilinear'

SCALER_H = os.environ.get('SCALER_H') or SCALER
SCALER_H = SCALER_H.lower()

SCALER_V = os.environ.get('SCALER_V') or SCALER
SCALER_V = SCALER_V.lower()

sys.stderr.write(f'Rendering {CARD.name}\n')
sys.stderr.write(f'Scaling mode: {SCALE}\n')
sys.stderr.write(f'Color conversion mode: {COLORCONV}\n')
sys.stderr.write(f'Clamping: {CLAMP}\n')
sys.stderr.write(f'Equalize: {EQUALIZE}\n')

clip = clip[CARD.frame]

# Nonlinearity precorrection
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444P8)
yclip, uclip, vclip = clip.std.SplitPlanes()

lut = [(-16, -16), (0, 0), (16, 16), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23),
       (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32),
       (32, 33), (33, 34), (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41),
       (41, 42), (42, 43), (43, 44), (44, 45.5), (45, 47), (46, 48), (47, 49), (48, 49.5), (49, 51),
       (50, 51.5), (51, 53), (52, 54), (53, 55), (54, 56), (55, 57), (56, 57.5), (57, 59),
       (58, 59.5), (59, 60), (60, 61.5), (61, 63), (62, 63.5), (63, 65), (64, 65.5), (65, 67),
       (66, 67.5), (67, 68.55555555555556), (68, 69.4), (69, 70.5), (70, 71.4), (71, 72.5),
       (72, 73.4), (73, 74.5), (74, 75.4), (75, 76.5), (76, 77.4), (77, 78.5), (78, 79.4),
       (79, 80.5), (80, 81.4), (81, 82.5), (82, 83.4), (83, 84.5), (84, 85.4), (85, 86.5),
       (86, 87.4), (87, 88.5), (88, 89.95), (89, 91.4), (90, 92.47368421052632),
       (91, 93.38095238095238), (92, 94.5), (93, 95.95), (94, 97.4), (95, 98.5), (96, 99.4),
       (97, 100.52380952380952), (98, 101.42105263157895), (99, 102.5), (100, 103.5), (101, 104.5),
       (102, 105.42105263157895), (104, 106.5), (105, 107.47619047619048), (106, 108.5),
       (107, 109.5), (108, 110.5), (109, 111.42105263157895), (110, 112.33333333333333),
       (111, 113.15), (112, 114.25), (113, 115.15), (114, 116.25), (116, 117.15), (117, 118.25),
       (118, 119.15), (119, 120.25), (120, 121.15), (121, 122.25), (122, 123.15),
       (123, 124.16666666666667), (124, 125.25), (125, 126.75), (126, 127.25), (128, 128.5),
       (129, 128.4), (130, 129.5), (131, 130), (132, 131.5), (133, 132), (134, 133.5), (135, 134),
       (136, 135.5), (137, 136), (138, 137), (139, 138), (140, 138), (141, 139), (142, 140),
       (143, 141), (144, 142), (145, 143), (146, 144), (147, 145.5), (148, 146), (149, 147),
       (150, 148), (152, 149.5), (153, 150), (154, 151.5), (155, 152), (156, 153), (157, 154),
       (158, 155), (159, 156), (160, 157.5), (161, 158), (162, 159.5), (164, 160), (165, 161.5),
       (166, 162), (167, 163.5), (168, 164), (169, 165.5), (170, 166), (171, 167.5), (172, 168),
       (173, 169.5), (174, 170), (175, 171.5), (176, 172), (177, 173.5), (178, 174), (179, 175),
       (180, 176), (181, 177), (182, 178), (183, 178), (184, 179.33333333333334), (185, 180),
       (186, 181), (187, 182), (188, 182.5), (189, 184), (190, 184.5), (191, 186), (192, 186.5),
       (193, 188), (194, 188.5), (195, 190), (196, 190.55), (197, 192), (198, 192.5), (199, 194),
       (200, 194.5), (201, 196), (202, 196.5), (203, 198), (204, 198.5), (205, 200), (206, 200.5),
       (207, 202), (208, 202.5), (209, 204), (210, 204.5), (211, 206), (212, 206.5), (213, 208),
       (214, 208.5), (215, 210), (216, 210.5), (217, 212), (218, 212.5), (219, 214), (220, 214.5),
       (221, 216), (222, 216.5), (223, 218), (224, 218.5), (225, 220), (226, 221), (227, 222),
       (228, 223), (230, 224.5), (231, 226.28571428571428), (232, 228.44444444444446), (233, 230.5),
       (234, 232.66666666666666), (235, 234.75), (236, 236.57142857142858), (237, 238), (240, 250),
       (243, 262), (250, 280), (255, 295), (260, 310)]

y_spline = scipy.interpolate.CubicSpline([inp for inp, outp in lut], [outp for inp, outp in lut],
                                         bc_type='clamped')


def correct_y(x):
    if EQUALIZE:
        result = float(y_spline(x))
        # Additional correction for SD content
        if COLORCONV is common.ColorConversion.FORCE601 or (
                COLORCONV is common.ColorConversion.AUTO and CARD.mode is not common.OriginalResolution.HD1080):
            if result > 223.0:
                result = (4.0 * result + 1115.0) / 9.0
    else:
        result = x
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
    scaler_h_kwargs = {}
    if SCALER_H[0:2] == 'de':
        scaler_h = getattr(vapoursynth.core.descale, SCALER_H[0].upper() + SCALER_H[1:])
        if dimensions.scale_w == dimensions.precrop_w:
            src_left = 0
        else:
            src_left *= -dimensions.scale_w / dimensions.precrop_w
        src_width = None
        scaler_h_kwargs = {'src_left': src_left}
    else:
        scaler_h = vapoursynth.core.placebo.Resample
        scaler_h_kwargs = {'filter': SCALER_H, 'sx': src_left}
        if ANTIRING != 0:
            scaler_h_kwargs['antiring'] = ANTIRING
    if SCALER_V[0:2] == 'de':
        scaler_v = getattr(vapoursynth.core.descale, SCALER_V[0].upper() + SCALER_V[1:])
        if dimensions.scale_h == clip.height:
            src_top = 0
        else:
            src_top *= -dimensions.scale_h / clip.height
        src_height = None
        scaler_v_kwargs = {'src_top': src_top}
    else:
        scaler_v = vapoursynth.core.placebo.Resample
        scaler_v_kwargs = {'filter': SCALER_V, 'sy': src_top}
        if ANTIRING != 0:
            scaler_v_kwargs['antiring'] = ANTIRING

    while dimensions.precrop_w > clip.width:
        rclip = vapoursynth.core.std.FlipHorizontal(clip)
        clip = vapoursynth.core.std.StackHorizontal([rclip, clip, rclip])
    if dimensions.precrop_w != clip.width:
        clip = vapoursynth.core.std.CropAbs(clip, dimensions.precrop_w, clip.height,
                                            left=(clip.width - dimensions.precrop_w) // 2)
    if SCALER_H == SCALER_V:
        clip = scaler_v(clip, dimensions.scale_w, dimensions.scale_h, src_width=src_width,
                        src_height=src_height, **(scaler_h_kwargs | scaler_v_kwargs))
    else:
        clip = scaler_h(clip, dimensions.scale_w, clip.height, src_width=src_width,
                        **scaler_h_kwargs)
        clip = scaler_v(clip, clip.width, dimensions.scale_h, src_height=src_height,
                        **scaler_v_kwargs)
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
    # It looks that the SD test cards have converted matrix, but not primaries
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT470_BG,
                                         transfer=vapoursynth.TRANSFER_BT709,
                                         primaries=vapoursynth.PRIMARIES_BT709)

# Output
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
clip.set_output()
