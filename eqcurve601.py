#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections

import PIL.Image
import numpy

tsimg = PIL.Image.open('TestCardWCalib.png')

tsdata = numpy.array(tsimg.get_flattened_data()).reshape((tsimg.height, tsimg.width, 3))

lut = collections.defaultdict(list)

for x in range(0, 895):
    inp = tsdata[1067, x, 1]
    outp = (208021.0 - 217.0 * x) / 890.0
    lut[int(inp)].append(outp)

result = []
for inp, outp in sorted(lut.items(), key=lambda x: x[0]):
    outval = float(numpy.average(outp))
    if outval == int(outval):
        outval = int(outval)
    result.append((inp, outval))

print(result)
