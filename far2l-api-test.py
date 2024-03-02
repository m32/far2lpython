#!/usr/bin/env vpython3
import sys
from far2l import PluginManager, pluginmanager as pm

sys.path.insert(1, 'plugins')

def f2s(s):
    return pm.ffi.string(s)

def s2f(s):
    return pm.ffi.new("wchar_t []", s)

@pm.ffi.callback('int(int, void *)')
def EditorControl(cmd, ei):
    print('EditorControl=', cmd, ei)
    if cmd == 6:
        ei = pm.ffi.cast('struct EditorInfo *', ei)
        ei.EditorID = 9999
        ei.TotalLines = 1
        print(ei)
    return 0

@pm.ffi.callback('int(wchar_t *, wchar_t *, int, int, int, int, uint32_t, int, int, unsigned int)')
def Editor(*args):
    print('Editor:', args)
    return 0

psi = pm.ffi.new('struct PluginStartupInfo *')
psi.EditorControl = EditorControl
psi.Editor = Editor

ppm = PluginManager()
ppm.SetStartupInfo(int(pm.ffi.cast('uint64_t', psi)))

pi = pm.ffi.new('struct PluginInfo *')
ppm.GetPluginInfo(int(pm.ffi.cast('uint64_t', pi)))
print('*'*20, 'GetPluginInfo')
for name in dir(pi):
    print(name, getattr(pi, name))

rc = ppm.OpenPlugin(pm.ffic.OPEN_COMMANDLINE, s2f('load uinfo'))
print('ppm.OpenPlugin(pm.ffic.OPEN_COMMANDLINE)=', rc)

ppm.GetPluginInfo(int(pm.ffi.cast('uint64_t', pi)))
print('*'*20, 'GetPluginInfo')
for name in dir(pi):
    print(name, getattr(pi, name))

rc = ppm.OpenPlugin(pm.ffic.OPEN_EDITOR, 0)
print('ppm.OpenPlugin(pm.ffic.OPEN_EDITOR)=', rc)
