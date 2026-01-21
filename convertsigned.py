#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct

with open('/dev/stdin', 'rb') as f:
    data = f.read()

values = [item[0] - 32768 for item in struct.iter_unpack('=H', data)]

with open('/dev/stdout', 'wb') as f:
    for item in values:
        f.write(struct.pack('=h', item))
