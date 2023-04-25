#!/usr/bin/env vpython3
import sys
from far2l import PluginManager, pluginmanager as pm

ps = '*adb://ZY3225879Q/*'
s1 = pm.ffi.new("wchar_t[]", ps)
s2 = pm.ffi.string(s1)
print(ps, s1, s2)