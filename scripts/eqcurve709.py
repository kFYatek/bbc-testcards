#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections

import PIL.Image
import numpy

if not 'get_flattened_data' in PIL.Image.Image.__dict__.keys():
    PIL.Image.Image.get_flattened_data = PIL.Image.Image.getdata


def _main():
    tsimg = PIL.Image.open('TestCardX.png')
    refimg = PIL.Image.open('Test-Card-X-Reference.jpg')

    tsdata = numpy.array(tsimg.get_flattened_data()).reshape((tsimg.height, tsimg.width, 3))
    refdata = numpy.array(refimg.get_flattened_data()).reshape((refimg.height, refimg.width, 3))

    lut = collections.defaultdict(list)

    inputs = [(1041, x, 1) for x in range(8, 912)] + [(1065, x, 1) for x in range(8, 920)]

    for coord in inputs:
        lut[int(tsdata[*coord])].append(int(refdata[*coord]))

    result = []
    for inp, outp in sorted(lut.items(), key=lambda x: x[0]):
        outval = float(numpy.average(outp))
        if outval == int(outval):
            outval = int(outval)
        result.append((inp, outval))

    print(result)


if __name__ == '__main__':
    _main()
