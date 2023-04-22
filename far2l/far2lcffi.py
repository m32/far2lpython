import cffi
ffi = cffi.FFI()
with open(__file__+'.cpp', 'rt') as fp:
    data = fp.read()
    ffi.cdef(data, packed=True)
del data, fp
