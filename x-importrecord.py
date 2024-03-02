#!/usr/bin/env vpython3
import sys
from ctypes import *
from far2l import PluginManager, pluginmanager as pm

dllname = './x-importrecord.so'
hdll = CDLL(dllname)

#import pdb; pdb.set_trace()
getrec = hdll.getrec
getrec.argtypes = []
getrec.restype = c_void_p

cir = getrec()
print('cir=%08X'%cir)

def show(ir):
    print('sizeof=', pm.ffi.sizeof('INPUT_RECORD'))
    print('Event=', ir.EventType)
    e = ir.Event.KeyEvent
    print('KeyDown=%04X'%e.bKeyDown)
    print('wRepeatCount=', e.wRepeatCount)
    print('wVirtualKeyCode=%08X'% e.wVirtualKeyCode)
    print('wVirtualScanCode=%08X'% e.wVirtualScanCode)
    print('uChar=', e.uChar.UnicodeChar)
    print('aChar=', e.uChar.AsciiChar)
    print('dwControlKeyState=%08X'% e.dwControlKeyState)

def main():
    print('*'*20, 'encode')
    hdll.encode()
    print('*'*20, 'decode')
    hdll.decode()
    print('*'*20, 'python')
    ir = pm.ffi.cast("INPUT_RECORD *", cir)
    show(ir)

print('main')
main()
print('done')
