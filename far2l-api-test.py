#!/usr/bin/env vpython3
import sys
from far2l import PluginManager, pluginmanager as pm

sys.path.insert(1, 'plugins')

def ptrto(s):
    return ct.cast(ct.byref(s), ct.c_void_p)

def f2s(s):
    return ct.c_wchar_p.from_buffer(s).value

def s2f(s):
    return ct.create_unicode_buffer(s)

def ctshow(msg, cls):
    print('*'*20, msg, cls.__class__.__name__,':')
    for fname, ftype in cls._fields_:
        value = getattr(cls, fname)
        print('   ', fname, value)

def EditorControl(cmd, ei):
    print('EditorControl=', cmd, ei)
    if cmd == 6:
        t = ct.POINTER(fct.struct_EditorInfo)
        ei = ct.cast(ei, t).contents
        ei.EditorID = 9999
        ei.TotalLines = 1
        print(ei)
    return 0

psi = fct.struct_PluginStartupInfo()
psi.EditorControl = fct.FARAPIEDITORCONTROL(EditorControl)

pm = PluginManager()
pm.SetStartupInfo(ptrto(psi))

pi = fct.struct_PluginInfo()
pm.GetPluginInfo(ct.byref(pi))
ctshow('GetPluginInfo', pi)

item = ct.create_unicode_buffer('load uinfo')
pm.OpenPlugin(fct.OPEN_COMMANDLINE, ptrto(item))

pm.GetPluginInfo(ct.byref(pi))
ctshow('GetPluginInfo', pi)
#print('plugin info:', f2s(pi.PluginMenuStrings[0]))

pm.OpenPlugin(fct.OPEN_EDITOR, 0)

v = pi.CommandPrefix
print(dir(v))
