#!/usr/bin/env python3

import sys

try:
    import ascii_painter_engine
except Exception as e:
    sys.path.insert(1, '..\\')
    print(sys.path)
    import ascii_painter_engine

print('success!')