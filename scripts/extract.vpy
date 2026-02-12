# -*- coding: utf-8 -*-
import os
import sys

import numpy
import scipy.interpolate
import vapoursynth

sys.path.insert(0, os.getcwd())
import common

del sys.path[0]
os.chdir(os.pardir)

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

lut601 = [(-16, -16), (0, 0), (16, 16), (17, 17.097191011235957), (18, 18.07247191011236),
          (19, 19.047752808988765), (20, 20.023033707865167), (21, 20.998314606741573),
          (22, 22.21741573033708), (23, 23.314606741573034), (24, 24.16797752808989),
          (25, 25.143258426966295), (26, 26.240449438202248), (27, 27.21573033707865),
          (28, 28.069101123595505), (29, 29.04438202247191), (30, 30.019662921348313),
          (31, 30.99494382022472), (32, 32.092134831460676), (33, 33.189325842696626),
          (34, 34.16460674157303), (35, 35.13988764044944), (36, 36.11516853932584),
          (37, 37.09044943820225), (38, 38.065730337078655), (39, 39.041011235955054),
          (40, 40.13820224719101), (41, 41.113483146067416), (42, 42.08876404494382),
          (43, 43.307865168539315), (44, 45.014606741573026), (45, 46.11179775280899),
          (46, 47.087078651685395), (47, 47.94044943820225), (48, 48.91573033707864),
          (49, 49.891011235955055), (50, 50.866292134831454), (51, 52.08539325842697),
          (52, 53.06067415730337), (53, 54.27977528089887), (54, 55.01123595505618),
          (55, 56.108426966292136), (56, 57.08370786516855), (57, 58.05898876404494),
          (58, 59.1561797752809), (59, 60.1314606741573), (60, 61.057977528089886),
          (61, 61.71629213483146), (62, 63.05730337078652), (63, 64.15449438202246),
          (64, 65.12977528089887), (65, 65.98314606741575), (66, 67.08033707865168),
          (67, 68.17752808988764), (68, 69.03089887640449), (69, 70.0061797752809),
          (70, 71.2252808988764), (71, 72.20056179775281), (72, 73.17584269662922),
          (73, 74.15112359550562), (74, 75.12640449438203), (75, 76.10168539325844),
          (76, 77.07696629213484), (77, 78.05224719101125), (78, 79.02752808988765),
          (79, 80.1247191011236), (80, 81.1), (81, 81.95337078651684), (82, 83.0505617977528),
          (83, 84.14775280898877), (84, 85.00112359550562), (85, 85.85449438202247),
          (86, 87.09101123595505), (87, 87.56123595505619), (88, 89.38988764044944),
          (89, 91.2185393258427), (90, 92.1938202247191), (91, 93.16910112359551),
          (92, 94.14438202247192), (93, 95.53957553058677), (94, 97.09460674157303),
          (95, 98.04550561797754), (96, 99.02078651685395), (97, 100.1179775280899),
          (98, 101.09325842696629), (99, 102.0685393258427), (100, 103.0438202247191),
          (101, 104.40921348314608), (102, 105.15692883895132), (103, 105.23820224719101),
          (104, 105.96966292134832), (105, 106.82303370786518), (106, 108.04213483146069),
          (107, 109.01741573033708), (108, 109.99269662921348), (109, 111.21179775280899),
          (110, 112.30898876404494), (111, 113.28426966292136), (112, 114.13764044943821),
          (113, 115.11292134831461), (114, 115.96629213483146), (115, 116.21011235955056),
          (116, 117.13662921348316), (117, 117.59176029962548), (118, 119.01404494382022),
          (119, 119.98932584269662), (120, 121.20842696629212), (121, 122.42752808988763),
          (122, 123.15898876404495), (123, 123.89044943820224), (124, 124.9876404494382),
          (125, 125.96292134831461), (126, 126.81629213483147), (127, 127.66966292134832),
          (128, 127.91348314606742), (129, 128.88876404494383), (130, 130.10786516853932),
          (131, 131.2050561797753), (132, 132.1803370786517), (133, 133.15561797752812),
          (134, 134.1308988764045), (135, 135.30936329588016), (136, 135.47191011235952),
          (137, 137.17865168539325), (138, 138.15393258426965), (140, 139.12921348314606),
          (141, 140.22640449438202), (142, 141.07977528089887), (143, 142.05505617977528),
          (144, 143.03033707865166), (145, 144.0056179775281), (146, 144.9808988764045),
          (147, 145.9561797752809), (148, 146.93146067415728), (149, 148.02865168539327),
          (150, 149.24775280898876), (152, 150.22303370786517), (153, 151.19831460674158),
          (154, 152.17359550561798), (155, 153.1488764044944), (156, 154.1241573033708),
          (157, 155.09943820224717), (158, 156.0747191011236), (159, 157.04999999999998),
          (160, 158.02528089887642), (161, 159.12247191011238), (162, 160.09775280898876),
          (163, 160.4634831460674), (164, 161.31685393258428), (165, 162.17022471910113),
          (166, 163.14550561797753), (167, 164.1207865168539), (168, 165.2179775280899),
          (169, 166.31516853932584), (170, 167.1685393258427), (171, 168.1438202247191),
          (172, 169.24101123595509), (173, 170.21629213483146), (174, 171.19157303370787),
          (175, 172.16685393258427), (176, 173.14213483146068), (177, 174.1174157303371),
          (178, 175.09269662921346), (179, 176.0679775280899), (180, 177.04325842696628),
          (181, 178.5061797752809), (182, 179.1644943820225), (184, 180.2129213483146),
          (185, 181.18820224719101), (186, 182.28539325842698), (187, 183.1387640449438),
          (188, 183.99213483146067), (189, 184.96741573033705), (190, 186.06460674157304),
          (191, 187.03988764044942), (192, 188.01516853932586), (193, 189.23426966292132),
          (194, 190.20955056179776), (195, 191.1848314606742), (196, 192.16011235955057),
          (197, 193.13539325842694), (198, 194.11067415730338), (199, 195.08595505617976),
          (200, 196.0612359550562), (201, 197.03651685393257), (202, 198.011797752809),
          (203, 199.10898876404494), (204, 200.2061797752809), (205, 201.1814606741573),
          (206, 202.1567415730337), (207, 203.13202247191012), (208, 204.1073033707865),
          (209, 205.0825842696629), (210, 206.0578651685393), (211, 206.91123595505618),
          (212, 208.00842696629212), (213, 209.22752808988764), (214, 210.20280898876405),
          (215, 211.17808988764045), (216, 212.15337078651686), (217, 213.12865168539324),
          (218, 214.10393258426967), (219, 215.07921348314605), (220, 216.05449438202248),
          (221, 217.02977528089886), (222, 218.24887640449438), (223, 219.22415730337076),
          (224, 220.1994382022472), (225, 221.17471910112357), (226, 222.15),
          (227, 223.12528089887638), (228, 223.97865168539326), (230, 225.14898876404496),
          (231, 225.8073033707865), (232, 227.27022471910115), (233, 228.24550561797753),
          (234, 229.22078651685396), (235, 230.19606741573034), (236, 231.17134831460677),
          (237, 232.14662921348315), (238, 233.12191011235953), (240, 235), (252, 250), (264, 265)]

lut709 = [(-16, -16), (0, 0), (16, 16), (17, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23),
          (23, 24), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32),
          (32, 33), (33, 34), (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41),
          (41, 42), (42, 43), (43, 44), (44, 45.5), (45, 47), (46, 48), (47, 49), (48, 49.5),
          (49, 51), (50, 51.5), (51, 53), (52, 54), (53, 55), (54, 56), (55, 57), (56, 57.5),
          (57, 59), (58, 59.5), (59, 60), (60, 61.5), (61, 63), (62, 63.5), (63, 65), (64, 65.5),
          (65, 67), (66, 67.5), (67, 68.55555555555556), (68, 69.4), (69, 70.5), (70, 71.4),
          (71, 72.5), (72, 73.4), (73, 74.5), (74, 75.4), (75, 76.5), (76, 77.4), (77, 78.5),
          (78, 79.4), (79, 80.5), (80, 81.4), (81, 82.5), (82, 83.4), (83, 84.5), (84, 85.4),
          (85, 86.5), (86, 87.4), (87, 88.5), (88, 89.95), (89, 91.4), (90, 92.47368421052632),
          (91, 93.38095238095238), (92, 94.5), (93, 95.95), (94, 97.4), (95, 98.5), (96, 99.4),
          (97, 100.52380952380952), (98, 101.42105263157895), (99, 102.5), (100, 103.5),
          (101, 104.5), (102, 105.42105263157895), (104, 106.5), (105, 107.47619047619048),
          (106, 108.5), (107, 109.5), (108, 110.5), (109, 111.42105263157895),
          (110, 112.33333333333333), (111, 113.15), (112, 114.25), (113, 115.15), (114, 116.25),
          (116, 117.15), (117, 118.25), (118, 119.15), (119, 120.25), (120, 121.15), (121, 122.25),
          (122, 123.15), (123, 124.16666666666667), (124, 125.25), (125, 126.75), (126, 127.25),
          (128, 128.5), (129, 128.4), (130, 129.5), (131, 130), (132, 131.5), (133, 132),
          (134, 133.5), (135, 134), (136, 135.5), (137, 136), (138, 137), (139, 138), (140, 138),
          (141, 139), (142, 140), (143, 141), (144, 142), (145, 143), (146, 144), (147, 145.5),
          (148, 146), (149, 147), (150, 148), (152, 149.5), (153, 150), (154, 151.5), (155, 152),
          (156, 153), (157, 154), (158, 155), (159, 156), (160, 157.5), (161, 158), (162, 159.5),
          (164, 160), (165, 161.5), (166, 162), (167, 163.5), (168, 164), (169, 165.5), (170, 166),
          (171, 167.5), (172, 168), (173, 169.5), (174, 170), (175, 171.5), (176, 172),
          (177, 173.5), (178, 174), (179, 175), (180, 176), (181, 177), (182, 178), (183, 178),
          (184, 179.33333333333334), (185, 180), (186, 181), (187, 182), (188, 182.5), (189, 184),
          (190, 184.5), (191, 186), (192, 186.5), (193, 188), (194, 188.5), (195, 190),
          (196, 190.55), (197, 192), (198, 192.5), (199, 194), (200, 194.5), (201, 196),
          (202, 196.5), (203, 198), (204, 198.5), (205, 200), (206, 200.5), (207, 202),
          (208, 202.5), (209, 204), (210, 204.5), (211, 206), (212, 206.5), (213, 208),
          (214, 208.5), (215, 210), (216, 210.5), (217, 212), (218, 212.5), (219, 214),
          (220, 214.5), (221, 216), (222, 216.5), (223, 218), (224, 218.5), (225, 220), (226, 221),
          (227, 222), (228, 223), (230, 224.5), (231, 226.28571428571428),
          (232, 228.44444444444446), (233, 230.5), (234, 232.66666666666666), (235, 234.75),
          (236, 236.57142857142858), (237, 238), (240, 250), (243, 262), (250, 280), (255, 295),
          (260, 310)]

lut = lut709

# Color space conversion
if COLORCONV is common.ColorConversion.FORCE601TO709:
    clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
    clip = vapoursynth.core.std.SetFrameProps(clip, _Matrix=vapoursynth.MATRIX_BT470_BG,
                                              _Transfer=vapoursynth.TRANSFER_BT601,
                                              _Primaries=vapoursynth.PRIMARIES_BT470_BG)
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT709,
                                         transfer=vapoursynth.TRANSFER_BT709,
                                         primaries=vapoursynth.PRIMARIES_BT709)
elif COLORCONV in (common.ColorConversion.FORCE601, common.ColorConversion.LINEAR) or (
        COLORCONV is common.ColorConversion.AUTO and CARD.mode is not common.OriginalResolution.HD1080):
    # It looks that the SD test cards have converted matrix, but not primaries
    clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
    clip = vapoursynth.core.resize.Point(clip, matrix=vapoursynth.MATRIX_BT470_BG,
                                         transfer=vapoursynth.TRANSFER_BT709,
                                         primaries=vapoursynth.PRIMARIES_BT709)
    lut = lut601

# Nonlinearity correction
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444P16)
yclip, uclip, vclip = clip.std.SplitPlanes()

y_spline = scipy.interpolate.CubicSpline(numpy.array([inp for inp, outp in lut]) * 256.0,
                                         numpy.array([outp for inp, outp in lut]) * 256.0,
                                         bc_type='clamped')


def correct_y(x):
    if EQUALIZE:
        result = float(y_spline(x))
    else:
        result = x
    if CLAMP:
        result = min(max(result, 4096.0), 60160.0)
    else:
        result = min(max(result, 0.0), 65280.0)
    return (result - 4096) / 56064.0


def correct_uv(x):
    result = x - 32768
    if CLAMP:
        result = min(max(result, -28672.0), 28672.0)
    else:
        result = min(max(result, -32768.0), 32512.0)
    return result / 57344.0


yclip = vapoursynth.core.std.Lut(yclip, function=correct_y, floatout=True)
uclip = vapoursynth.core.std.Lut(uclip, function=correct_uv, floatout=True)
vclip = vapoursynth.core.std.Lut(vclip, function=correct_uv, floatout=True)

clip = vapoursynth.core.std.ShufflePlanes([yclip, uclip, vclip], planes=[0, 0, 0],
                                          colorfamily=vapoursynth.YUV, prop_src=clip)

if COLORCONV is common.ColorConversion.LINEAR:
    clip = vapoursynth.core.resize.Point(clip, transfer=vapoursynth.TRANSFER_LINEAR)

# Resizing
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

    clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
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

# Output
clip = vapoursynth.core.resize.Point(clip, format=vapoursynth.YUV444PS)
clip.set_output()
