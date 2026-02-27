#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import math
import sys

import matplotlib.pyplot
import matplotlib.widgets
import numpy

import common


def _main(*args):
    parser = argparse.ArgumentParser(
        description='Convert an initially preprocessed image to a more usable format.')
    parser.add_argument('input_file', type=str,
                        help='Input file. May be any format supported by PIL or raw{16|float}:[filename@]{width}x{height} - if no filename is specified for raw, it\'s read from stdin.')
    parser.add_argument('--channel', type=str, default='Y', help='Channel to plot, one of YUVRGB.')
    parser.add_argument('--input-colorspace', type=lambda x: common.ColorSpace(int(x)),
                        help=f'Color space to use when converting input to YUV {list(common.ColorSpace)}. Default is BT.601 for PIL input and YUV for raw input.')
    parser.add_argument('--output-colorspace', type=lambda x: common.ColorSpace(int(x)),
                        default=common.ColorSpace.BT601,
                        help=f'Color space to use when converting to RGB when plotting RGB channels. Default is BT.601.')
    parser.add_argument('--black', type=float, default=0.0,
                        help='Value on the Y axis to use as black level.')
    parser.add_argument('--white', type=float, default=1.0,
                        help='Value on the Y axis to use as white level.')
    args = parser.parse_args(args)

    data = common.load_and_process_image(args.input_file, args.input_colorspace)
    if args.channel == 'Y':
        data = data[:, :, 0]
    elif args.channel == 'U':
        data = data[:, :, 1]
    elif args.channel == 'V':
        data = data[:, :, 2]
    else:
        assert args.output_colorspace is not common.ColorSpace.YUV
        data = numpy.matvec(args.output_colorspace.to_rgb_matrix, data, axes=[(0, 1), 2, 2])
        if args.channel == 'R':
            data = data[:, :, 0]
        elif args.channel == 'G':
            data = data[:, :, 1]
        elif args.channel == 'B':
            data = data[:, :, 2]
        else:
            raise Exception('Invalid channel')

    if data.shape[0] <= 405:
        orig_resolution = common.OriginalResolution.SYSA43
    elif data.shape[0] <= 625:
        orig_resolution = common.OriginalResolution.PAL43
    elif data.shape[0] == 1080:
        orig_resolution = common.OriginalResolution.HD1080
    else:
        orig_resolution = None

    sample_rate_mhz = None
    if orig_resolution is not None:
        for scaling_mode in common.ScalingMode:
            if scaling_mode is not common.ScalingMode.NONE:
                candidate = common.get_scaling_dimensions(scaling_mode, orig_resolution)
                if candidate.crop_w == data.shape[1]:
                    sample_rate_mhz = candidate.sample_rate_mhz
                    break

    UPSAMPLE = 32
    data = common.resample_with_mirrors(data, data.shape[1] * UPSAMPLE)
    xdata = numpy.array(range(data.shape[1])) / UPSAMPLE

    def plotscale(value):
        return value * (args.white - args.black) + args.black

    fig = matplotlib.pyplot.figure()
    subplot = fig.add_subplot()
    subplot.set_autoscalex_on(True)
    subplot.set_autoscaley_on(False)
    if args.channel in ('U', 'V'):
        subplot.set_ybound(plotscale(-0.6), plotscale(0.6))
    else:
        subplot.set_ybound(plotscale(-0.1), plotscale(1.1))
    matplotlib.pyplot.subplots_adjust(bottom=0.25)

    lineno = 0
    mpline, = subplot.plot(xdata, plotscale(data[lineno]))
    mpdots, = subplot.plot(xdata[0::UPSAMPLE], plotscale(data[lineno, 0::UPSAMPLE]), 'o',
                           markersize=1, color=mpline.get_color())

    slider_frame = matplotlib.pyplot.axes((0.1, 0.1, 0.8, 0.03))
    slider = matplotlib.widgets.Slider(slider_frame, 'Line', 0, data.shape[0] - 1, valinit=0,
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
        nonlocal freq
        left, right = subplot.get_xlim()
        left = max(int(math.floor(left * UPSAMPLE)), 0)
        right = min(int(math.ceil(right * UPSAMPLE)), data.shape[1] - 1)
        mpdots.set_markersize(min(data.shape[1] / (right - left), 5))
        if left == right:
            freq = None
        else:
            inp = data[lineno][left:right + 1]
            fft = numpy.fft.rfft(inp - numpy.mean(inp))
            domf = numpy.argmax(numpy.abs(fft))
            if 0 < domf < len(fft) - 1:
                domf_pre = numpy.abs(fft[domf - 1])
                domf_peak = numpy.abs(fft[domf])
                domf_post = numpy.abs(fft[domf + 1])
                # Parabolic interpolation
                if domf_pre != 0 and domf_peak != 0 and domf_post != 0:
                    domf = domf + numpy.log(domf_pre / domf_post) / numpy.log(
                        domf_pre * domf_pre * domf_post * domf_post / (
                                domf_peak * domf_peak * domf_peak * domf_peak))
            freq = domf * UPSAMPLE / len(inp)
        update_title()

    def slider_update(val):
        nonlocal lineno
        lineno = int(numpy.floor(slider.val))
        mpline.set_ydata(plotscale(data[lineno]))
        mpdots.set_ydata(plotscale(data[lineno, 0::UPSAMPLE]))
        subplot.relim()
        matplotlib.pyplot.draw()
        measure_frequency(None)

    subplot.callbacks.connect('xlim_changed', measure_frequency)
    slider.on_changed(slider_update)
    slider_update(0)
    matplotlib.pyplot.show()


if __name__ == "__main__":
    sys.exit(_main(*sys.argv[1:]))
