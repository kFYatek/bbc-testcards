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
