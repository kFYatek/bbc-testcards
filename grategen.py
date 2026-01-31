#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys

import numpy

SAMPLERATE = float(sys.argv[1])
FREQUENCY = float(sys.argv[2])
MINIMUM = float(sys.argv[3])
MAXIMUM = float(sys.argv[4])
try:
    STARTPHASE = float(sys.argv[5])
except Exception:
    STARTPHASE = 0.0
try:
    STARTSHIFT = float(sys.argv[6])
except Exception:
    STARTSHIFT = 0.0
try:
    SLOPEFREQ = float(sys.argv[7])
except Exception:
    SLOPEFREQ = FREQUENCY

PHASE_FIRST = STARTPHASE + 0.25 + ((-512.0 - STARTSHIFT) * FREQUENCY) / SAMPLERATE
PHASE_LAST = STARTPHASE + 0.25 + ((511.0 - STARTSHIFT) * FREQUENCY) / SAMPLERATE

args = numpy.linspace(PHASE_FIRST, PHASE_LAST, 1024) % 1.0

if SLOPEFREQ < FREQUENCY:
    raise Exception('Invalid slope frequency')
elif SLOPEFREQ != FREQUENCY:
    slope = FREQUENCY / SLOPEFREQ
    for i in range(len(args)):
        if args[i] < 0.25 * slope:
            args[i] /= slope
        elif args[i] < 0.5 - 0.25 * slope:
            args[i] = 0.25
        elif args[i] < 0.5 + 0.25 * slope:
            args[i] = (args[i] - 0.5) / slope + 0.5
        elif args[i] < 1.0 - 0.25 * slope:
            args[i] = 0.75
        else:
            args[i] = (args[i] - 1.0) / slope + 1.0

line = numpy.sin(args * 2.0 * numpy.pi)
line = numpy.round(((line + 1.0) * 0.5 * (MAXIMUM - MINIMUM) + MINIMUM) * 56064.0 + 4096.0)

outbuf = bytearray(128 * 1024 * 2)
output = numpy.ndarray((128, 1024), dtype=numpy.uint16, buffer=outbuf)
output[:] = line

subprocess.run(['magick', '-size', '1024x128', '-depth', '16', 'gray:-', 'png:-'], input=outbuf,
               check=True)
