# -*- coding: utf-8 -*-
import argparse
import math
import weakref

import numpy
import scipy.fft


def fft_resampler(x: numpy.ndarray, num: int, shift: float = 0.0, axis: int = 0) -> numpy.ndarray:
    if axis < 0:
        axis = len(x.shape) + axis
    oldsize = x.shape[axis]
    intshift = int(numpy.round(shift))
    floatshift = shift - intshift

    if oldsize != num or floatshift != 0.0:
        smallersize = min(num, oldsize)
        fft = scipy.fft.rfft(numpy.swapaxes(x, len(x.shape) - 1, axis))[..., :smallersize // 2 + 1]
        if smallersize % 2 == 0:
            if num < oldsize:
                fft[..., -1] *= 2
            elif num > oldsize:
                fft[..., -1] *= 0.5
        if floatshift != 0.0:
            fft *= numpy.exp(numpy.linspace(0, 2.0j * floatshift * numpy.pi * (fft.shape[-1] / num),
                                            fft.shape[-1], endpoint=False))
        x = scipy.fft.irfft(fft * (num / oldsize), n=num)
        x = x.swapaxes(len(x.shape) - 1, axis)

    if intshift != 0:
        x = numpy.roll(x, -intshift, axis=axis)
    return x


class KernelResampler:
    def __init__(self, kernel=None, kernel_radius=None, aliased=False):
        super().__init__()
        if kernel is not None:
            self.kernel = kernel
        if kernel_radius is not None:
            self.kernel_radius = kernel_radius
        self.aliased = aliased

    def __call__(self, x: numpy.ndarray, num: int, shift: float = 0.0,
                 axis: int = 0) -> numpy.ndarray:
        if axis < 0:
            axis = len(x.shape) + axis
        oldsize = x.shape[axis]
        if num == oldsize and shift == 0.0:
            pass
        else:
            x = x.swapaxes(len(x.shape) - 1, axis)
            downsample = (not self.aliased and num < oldsize)
            args = numpy.linspace(0, oldsize, num, endpoint=False)
            args = (args + (shift * oldsize) / num)
            radius = (self.kernel_radius * oldsize) / num if downsample else self.kernel_radius
            min_kernels = args - radius
            min_kernels = numpy.int32(numpy.ceil(numpy.nextafter(min_kernels, numpy.inf)))
            max_kernels = args + radius
            max_kernels = numpy.int32(numpy.floor(numpy.nextafter(max_kernels, -numpy.inf)))
            output = numpy.zeros(list(x.shape[:-1]) + [num])
            scale = num / oldsize if downsample else 1.0
            for i in range(num):
                weight_sum = 0.0
                for j in range(min_kernels[i], max_kernels[i] + 1):
                    weight = self.kernel((j - args[i]) * scale)
                    weight_sum += weight
                    output[..., i] += weight * x[..., j % x.shape[-1]]
                if downsample and weight_sum != 0.0:
                    output[..., i] /= weight_sum
            x = output.swapaxes(len(output.shape) - 1, axis)
        return x


class LinearResampler(KernelResampler):
    kernel_radius = 1

    def kernel(self, x):
        return numpy.maximum(1.0 - numpy.abs(x), 0.0)


class CubicResampler(KernelResampler):
    kernel_radius = 2

    def __init__(self, a: float = -0.5, aliased: bool = False):
        super().__init__(aliased=aliased)
        self.a = a

    def kernel(self, x):
        if not isinstance(x, numpy.ndarray):
            x = numpy.array(x)
        origshape = x.shape
        if len(x.shape) == 0:
            x = numpy.array([x])
        output = numpy.zeros(x.shape)
        indices = numpy.abs(x) <= 1.0
        inp = numpy.abs(x[indices])
        output[indices] = (self.a + 2.0) * inp * inp * inp - (self.a + 3.0) * inp * inp + 1.0
        indices = (numpy.abs(x) < 2.0) ^ indices
        inp = numpy.abs(x[indices])
        output[indices] = self.a * inp * inp * inp - (5.0 * self.a) * inp * inp + (
                8.0 * self.a) * inp - 4.0 * self.a
        return numpy.reshape(output, origshape)


class AliasedResampler:
    def __init__(self, backend=fft_resampler):
        super(AliasedResampler, self).__init__()
        self._backend = backend

    def __call__(self, x: numpy.ndarray, num: int, shift: float = 0.0,
                 axis: int = 0) -> numpy.ndarray:
        if axis < 0:
            axis = len(x.shape) + axis
        oldsize = x.shape[axis]
        if num == oldsize and shift == 0.0:
            pass
        elif num > oldsize:
            x = self._backend(x, num, shift, axis)
        else:
            x = x.swapaxes(len(x.shape) - 1, axis)
            k = max(int(math.ceil(oldsize / num)), 2)
            x = self._backend(x, k * num, k * shift, -1)
            x = x[..., 0::k]
            x = x.swapaxes(len(x.shape) - 1, axis)
        return x


class HybridResampler:
    def __init__(self, backend_lo=CubicResampler(), backend_hi=fft_resampler, threshold=0.0078125,
                 mean_size=None):
        assert mean_size is None or mean_size >= 2
        super(HybridResampler, self).__init__()
        self.backend_lo = backend_lo
        self.backend_hi = backend_hi
        self.threshold = threshold
        self.mean_size = mean_size

    def __call__(self, x: numpy.ndarray, num: int, shift: float = 0.0,
                 axis: int = 0) -> numpy.ndarray:
        if axis < 0:
            axis = len(x.shape) + axis
        oldsize = x.shape[axis]
        if num == oldsize and shift == 0.0:
            pass
        else:
            x = x.swapaxes(len(x.shape) - 1, axis)
            resampled_hi = self.backend_hi(x, num, shift, -1)
            resampled_lo = self.backend_lo(x, num, shift, -1)
            means = numpy.zeros(x.shape)
            mean_size = self.mean_size
            if mean_size is None:
                if num >= oldsize:
                    mean_size = 3
                else:
                    mean_size = int(round(3 * (oldsize / num)))
            for i in range(oldsize):
                means[..., (i + mean_size // 2) % oldsize] = numpy.mean(
                    numpy.roll(x, -i, axis=-1)[..., :mean_size], axis=-1)
            lo_samples = numpy.float64(numpy.abs(x - means) < self.threshold)
            lo_samples = LinearResampler()(lo_samples, num, shift, -1)
            lo_samples = 0.5 - 0.5 * numpy.cos(lo_samples * numpy.pi)
            x = lo_samples * resampled_lo + (1.0 - lo_samples) * resampled_hi
            x = x.swapaxes(len(x.shape) - 1, axis)
        return x


RESAMPLERS = {'fft': lambda: fft_resampler,  #
              'linear': LinearResampler,  #
              'cubic': CubicResampler,  #
              'aliased': AliasedResampler,  #
              'hybrid': HybridResampler,  #
              }


def from_str(s: str):
    return RESAMPLERS[s.lower()]()


def add_argparse_arguments(parser: argparse.ArgumentParser, default='fft', axes='hv'):
    class StoreAxisResamplerAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            super(StoreAxisResamplerAction, self).__init__(*args, **kwargs)
            self.fired_namespaces = set()

        def __call__(self, parser, namespace, values, option_string=None):
            resampler = from_str(values)
            setattr(namespace, self.dest, resampler)
            nsid = id(namespace)
            self.fired_namespaces.add(nsid)
            weakref.ref(namespace, lambda w: self.fired_namespaces.remove(nsid))

    class StoreResamplerAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            for action in parser._actions:
                if isinstance(action, StoreAxisResamplerAction) and id(
                        namespace) in action.fired_namespaces:
                    raise Exception(
                        '--resampler and per-axis resampler options can\'t be used together')
            resampler = from_str(values)
            if len(axes) >= 2:
                for action in parser._actions:
                    if isinstance(action, StoreAxisResamplerAction):
                        setattr(namespace, action.dest, resampler)
            else:
                setattr(namespace, self.dest, resampler)

    default_obj = from_str(default)
    parser.add_argument('--resampler', default=default_obj if len(axes) < 2 else None,
                        action=StoreResamplerAction,
                        help=f'Algorithm to use for resampling, supported values: {(*RESAMPLERS.keys(),)}, default: {default}')
    if len(axes) >= 2:
        for axis in axes:
            parser.add_argument(f'--{axis}-resampler', default=default_obj,
                                action=StoreAxisResamplerAction,
                                help=f'Algorithm to use for resampling along the {axis.upper()} axis, supported values: {(*RESAMPLERS.keys(),)}, default: {default}')
