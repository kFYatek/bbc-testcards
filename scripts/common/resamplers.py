# -*- coding: utf-8 -*-
import math

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
