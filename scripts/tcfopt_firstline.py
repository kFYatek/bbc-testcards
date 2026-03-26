#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy


def _main():
    outbuf = bytearray(720 * 8)
    output = numpy.ndarray((720,), dtype=numpy.float64, buffer=outbuf)
    output[:] = numpy.concatenate(
        (numpy.zeros((441,)), 0.5 - 0.5 * numpy.cos(numpy.linspace(0, numpy.pi, 8, endpoint=False)),
         numpy.ones((271,))))
    with open('/dev/stdout', 'wb') as f:
        f.write(outbuf)


if __name__ == '__main__':
    _main()
