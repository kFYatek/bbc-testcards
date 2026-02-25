#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import os

import PIL.Image
import numpy

import common

if not 'get_flattened_data' in PIL.Image.Image.__dict__.keys():
    PIL.Image.Image.get_flattened_data = PIL.Image.Image.getdata


def _main():
    try:
        COLORSPACE = common.ColorSpace(int(os.environ.get('COLORSPACE')))
    except Exception:
        COLORSPACE = common.ColorSpace.BT601
    LIMITED = bool(int(os.environ.get('LIMITED') or '0'))
    RAW16IN = int(os.environ.get('RAW16IN') or '0')
    RAW16OUT = bool(int(os.environ.get('RAW16OUT') or '0'))
    FILEIN = os.environ.get('FILEIN')
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

    if FILEIN is not None:
        image = PIL.Image.open(FILEIN)
        width = image.width
        height = image.height
        if image.mode.startswith('I;16'):
            rgbdata = numpy.array(image.get_flattened_data())
            rgbdata = rgbdata.reshape((1, height, width))
            rgbdata = (rgbdata - 4096.0) / 56064.0
            rgbdata = rgbdata.repeat(3, axis=0)
        else:
            image = image.convert('RGB')
            rgbdata = numpy.array(image.get_flattened_data())
            rgbdata = rgbdata.reshape((height, width, 3))
            rgbdata = (rgbdata - 16.0) / 219.0
            rgbdata = rgbdata.transpose((2, 0, 1))
        yuvdata = numpy.matvec(COLORSPACE.from_rgb_matrix, rgbdata, axes=[(0, 1), (0), (0)])
        COLORSPACE = common.ColorSpace.YUV
    else:
        with open('/dev/stdin', 'rb') as f:
            data = f.read()

        multiplier = 6 if RAW16IN > 0 else 12
        if len(data) == multiplier * 1920 * 1080:
            width = 1920
            height = 1080
        elif len(data) % (multiplier * 576) == 0 and len(data) // (multiplier * 576) >= 720:
            width = len(data) // (multiplier * 576)
            height = 576
        elif len(data) % (multiplier * 378) == 0 and len(data) // (multiplier * 378) >= 486:
            width = len(data) // (multiplier * 378)
            height = 378

        if RAW16IN > 0:
            yuvdata_raw = numpy.ndarray((height, width, 3), dtype=numpy.uint16,
                                        buffer=bytearray(data))
        else:
            yuvdata_raw = numpy.ndarray((3, height, width), dtype=numpy.float32,
                                        buffer=bytearray(data))
        yuvdata = numpy.zeros(yuvdata_raw.shape)
        yuvdata[:, :, :] = yuvdata_raw

        if RAW16IN == 1:
            yuvdata = numpy.transpose(yuvdata, (2, 0, 1))
            yuvdata /= 256.0
            yuvdata[0] -= 16.0
            yuvdata[0] /= 219.0
            yuvdata[1:] -= 128.0
            yuvdata[1:] /= 224.0
        elif RAW16IN == 2:
            rgbdata = numpy.transpose(yuvdata, (2, 0, 1))
            rgbdata = (rgbdata - 4096.0) / (219.0 * 256.0)
            yuvdata = numpy.matvec(COLORSPACE.from_rgb_matrix, rgbdata, axes=[(0, 1), (0), (0)])
            COLORSPACE = common.ColorSpace.YUV

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
    _main()
