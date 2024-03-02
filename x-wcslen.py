#!/usr/bin/env vpython3
from ctypes import *

import cffi
ffi = cffi.FFI()

s = '*adb://ZY3225879Q/acct*'
w = ffi.new("wchar_t[]", s)
p = ffi.cast('unsigned char *', w)
for i in range(0, len(s)*4+8, 16):
    s = [c for c in p[i:i+16]]
    c = bytes([s[x] for x in range(0, len(s), 4)])
    print(s, c)
