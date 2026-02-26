#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import enum
import math
import os
import sys

import PIL.Image
import numpy

import common


class InputFormat(enum.Enum):
    YUV = 0
    RGB = 1


def _main(*args):
    try:
        COLORSPACE = common.ColorSpace(int(os.environ.get('COLORSPACE')))
    except Exception:
        COLORSPACE = common.ColorSpace.BT601
    LIMITED = bool(int(os.environ.get('LIMITED') or '0'))
    RAW16OUT = bool(int(os.environ.get('RAW16OUT') or '0'))
    PLOT = int(os.environ.get('PLOT') or '0')
    PLOTSCALE = float(os.environ.get('PLOTSCALE') or '1')

    try:
        CARD = common.CARDS[int(os.environ['CARD'])]
    except Exception:
        CARD = None

    try:
        SCALE = common.ScalingMode(int(os.environ.get('SCALE')))
    except Exception:
        SCALE = common.ScalingMode.NONE

    parser = argparse.ArgumentParser(
        description='Convert an initially preprocessed image to a more usable format.')
    parser.add_argument('input_file', type=str,
                        help='Input file. May be any format supported by PIL or raw{16|float}:[filename@]{width}x{height} - if no filename is specified for raw, it\'s read from stdin.')
    parser.add_argument('--input-format', type=lambda x: InputFormat(int(x)),
                        help=f'Input format {list(InputFormat)}. Default is RGB for PIL input and YUV for raw input.')
    args = parser.parse_args(args)

    def infer_dimensions(samples):
        if samples % 1080 == 0 and samples // 1080 >= 1440:
            return samples // 1080, 1080
        elif samples % 576 == 0 and samples // 576 >= 720:
            return samples // 576, 576
        elif samples % 378 == 0 and samples // 378 >= 486:
            return samples // 378, 378

    data, data_range = common.read_image(args.input_file, infer_dimensions)
    input_format = args.input_format
    if input_format is None:
        if ':' in args.input_file and args.input_file.startswith('raw'):
            input_format = InputFormat.YUV
        else:
            input_format = InputFormat.RGB

    width = data.shape[1]
    height = data.shape[0]
    data = data.transpose((2, 0, 1))

    if input_format == InputFormat.RGB:
        if data.shape[0] == 1:
            data = data.repeat(3, axis=2)
        if data_range == 65535:
            data = (data - 4096.0) / 56064.0
        elif data_range == 255:
            data = (data - 16.0) / 219.0
        else:
            assert data_range == 1
        yuvdata = numpy.matvec(COLORSPACE.from_rgb_matrix, data, axes=[(0, 1), (0), (0)])
        COLORSPACE = common.ColorSpace.YUV
    else:
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

    dimensions = None
    src_left = 0.0
    src_top = 0.0
    if CARD is not None:
        dimensions = common.get_scaling_dimensions(SCALE, CARD.mode)
        if width >= common.get_scaling_dimensions(common.ScalingMode.VERTICAL, CARD.mode).crop_w:
            src_left = CARD.src_left
        if height == 1080:
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

    yuvdata = common.apply_shift(yuvdata, src_left, axis=2)
    yuvdata = common.apply_shift(yuvdata, src_top, axis=1)

    if dimensions is not None:
        yuvdata = common.resample_with_mirrors(yuvdata, dimensions.scale_w, axis=2)
        yuvdata = common.resample_with_mirrors(yuvdata, dimensions.scale_h, axis=1)
        if dimensions.crop_w != dimensions.scale_w:
            yuvdata = yuvdata[:, :, (yuvdata.shape[2] - dimensions.crop_w) // 2:]
            yuvdata = yuvdata[:, :, :dimensions.crop_w]

    outdata = numpy.matvec(COLORSPACE.to_rgb_matrix, yuvdata, axes=[(0, 1), (0), (0)])

    if PLOT > 0:
        import matplotlib.pyplot
        import matplotlib.widgets

        if dimensions is None:
            if CARD is not None:
                orig_resolution = CARD.mode
            elif height <= 405:
                orig_resolution = common.OriginalResolution.SYSA43
            elif height <= 625:
                orig_resolution = common.OriginalResolution.PAL43
            elif height == 1080:
                orig_resolution = common.OriginalResolution.HD1080
            else:
                orig_resolution = None

            if orig_resolution is not None:
                for scaling_mode in common.ScalingMode:
                    if scaling_mode is not common.ScalingMode.NONE:
                        candidate = common.get_scaling_dimensions(scaling_mode, orig_resolution)
                        if candidate.crop_w == outdata.shape[2]:
                            dimensions = candidate
                            break

        if dimensions is not None:
            sample_rate_mhz = dimensions.sample_rate_mhz
        else:
            sample_rate_mhz = None

        UPSAMPLE = 32
        outdata = common.resample_with_mirrors(outdata, outdata.shape[2] * UPSAMPLE, axis=2)
        xdata = numpy.array(range(outdata.shape[2])) / UPSAMPLE

        fig = matplotlib.pyplot.figure()
        subplot = fig.add_subplot()
        subplot.set_autoscalex_on(True)
        subplot.set_autoscaley_on(False)
        if PLOT == 1 or COLORSPACE is not common.ColorSpace.YUV:
            subplot.set_ybound(-0.1 * PLOTSCALE, 1.1 * PLOTSCALE)
        else:
            subplot.set_ybound(-0.6 * PLOTSCALE, 0.6 * PLOTSCALE)
        matplotlib.pyplot.subplots_adjust(bottom=0.25)

        lineno = 0
        mpline, = subplot.plot(xdata, outdata[PLOT - 1, lineno] * PLOTSCALE)
        mpline2, = subplot.plot(xdata[0::UPSAMPLE], outdata[PLOT - 1, lineno, 0::UPSAMPLE], 'o',
                                markersize=1)

        slider_frame = matplotlib.pyplot.axes([0.1, 0.1, 0.8, 0.03])
        slider = matplotlib.widgets.Slider(slider_frame, 'Line', 0, outdata.shape[1] - 1, valinit=0,
                                           valfmt='%d')

        lineno = 0
        freq = None

        def update_title():
            title = f'Line {lineno}'
            if freq is not None:
                freq_text = f'{freq:.6g} * fS'
                if sample_rate_mhz is not None:
                    freq_text = f'{freq * sample_rate_mhz:.6g} MHz ({freq_text})'
                title += ' || Dominant frequency: ' + freq_text
            subplot.set_title(title)

        def measure_frequency(axes):
            global freq
            left, right = subplot.get_xlim()
            left = max(int(math.floor(left * UPSAMPLE)), 0)
            right = min(int(math.ceil(right * UPSAMPLE)), outdata.shape[2] - 1)
            mpline2.set_markersize(min(outdata.shape[2] / (right - left), 5))
            if left == right:
                freq = None
            else:
                input = outdata[PLOT - 1, lineno][left:right + 1]
                fft = numpy.fft.rfft(input - numpy.mean(input))
                domf = numpy.argmax(numpy.abs(fft))
                if domf > 0 and domf < len(fft) - 1:
                    domf_pre = numpy.abs(fft[domf - 1])
                    domf_peak = numpy.abs(fft[domf])
                    domf_post = numpy.abs(fft[domf + 1])
                    # Parabolic interpolation
                    if domf_pre != 0 and domf_peak != 0 and domf_post != 0:
                        domf = domf + numpy.log(domf_pre / domf_post) / numpy.log(
                            domf_pre * domf_pre * domf_post * domf_post / (
                                    domf_peak * domf_peak * domf_peak * domf_peak))
                freq = domf * UPSAMPLE / len(input)
            update_title()

        def slider_update(val):
            global lineno
            lineno = int(numpy.floor(slider.val))
            mpline.set_ydata(outdata[PLOT - 1, lineno] * PLOTSCALE)
            mpline2.set_ydata(outdata[PLOT - 1, lineno, 0::UPSAMPLE] * PLOTSCALE)
            subplot.relim()
            matplotlib.pyplot.draw()
            measure_frequency(None)

        subplot.callbacks.connect('xlim_changed', measure_frequency)
        slider.on_changed(slider_update)
        slider_update(0)
        matplotlib.pyplot.show()
    else:
        if LIMITED or RAW16OUT:
            if COLORSPACE is not common.ColorSpace.YUV:
                outdata *= 219.0
                outdata += 16.0
            else:
                outdata[0] *= 219.0
                outdata[0] += 16.0
                outdata[1:] *= 224.0
                outdata[1:] += 128.0
            if RAW16OUT:
                outdata *= 256.0
        else:
            if COLORSPACE is common.ColorSpace.YUV:
                outdata[1:] += 0.5
            outdata *= 255.0

        outdata = numpy.transpose(outdata, (1, 2, 0))
        outbuf = bytearray(outdata.size * (2 if RAW16OUT else 1))
        output = numpy.ndarray(outdata.shape, dtype='uint16' if RAW16OUT else 'uint8',
                               buffer=outbuf)
        output[:, :, :] = numpy.round(
            numpy.minimum(numpy.maximum(outdata, 0.0), 65535.0 if RAW16OUT else 255.0))

        with open('/dev/stdout', 'wb') as f:
            if RAW16OUT:
                f.write(outbuf)
            else:
                PIL.Image.frombuffer('RGB', (output.shape[1], output.shape[0]), outbuf).save(f,
                                                                                             format='PNG')


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
