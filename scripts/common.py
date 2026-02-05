# -*- coding: utf-8 -*-
import enum
import typing


class ColorSpace(enum.Enum):
    YUV = 0
    BT601 = 601
    BT709 = 709


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


def get_scaling_dimensions(scaling_mode: ScalingMode, original_resolution: OriginalResolution) -> \
        typing.Optional[ScalingDimensions]:
    if scaling_mode is ScalingMode.NONE or original_resolution is OriginalResolution.HD1080:
        return None

    if scaling_mode is ScalingMode.VERTICAL:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(2560, 2560, 1970, 576)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 1920, 1478, 576)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1920, 1920, 1478, 378)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1920, 1920, 1386, 378)
    elif scaling_mode is ScalingMode.CANONICAL:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(2560, 936, 720, 576)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 936, 720, 576)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1920, 936, 720, 378)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1400, 728, 720, 378)
    elif scaling_mode is ScalingMode.SQUARE_PIXELS:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(1980, 1056, 1052, 576)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(1920, 1024, 788, 576)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(1480, 518, 518, 378)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(1400, 490, 486, 378)
    elif scaling_mode is ScalingMode.PAL_4FSC:
        if original_resolution is OriginalResolution.PAL169:
            return ScalingDimensions(12288, 5902, 946, 576)
        elif original_resolution is OriginalResolution.PAL43:
            return ScalingDimensions(9216, 5902, 946, 576)
        elif original_resolution is OriginalResolution.SYSA43:
            return ScalingDimensions(9216, 5902, 946, 378)
        elif original_resolution is OriginalResolution.SYSA54:
            return ScalingDimensions(8640, 5902, 946, 378)


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
