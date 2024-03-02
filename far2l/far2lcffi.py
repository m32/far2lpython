import cffi
ffi = cffi.FFI()
pack = None
with open(__file__+'.cpp', 'rt') as fp:
    data = fp.read()
while True:
    i = data.find('//#pragma pack')
    if i < 0:
        ffi.cdef(data, pack=pack)
        break
    ndata = data[:i]
    ffi.cdef(ndata, pack=pack)
    data = data[i:]
    i = data.find(')')
    s = data[:i+1]
    if s.find('()') > 0:
        pack = None
    else:
        pack = 2
    data = data[i+1:]
del pack, data, i, ndata, s
