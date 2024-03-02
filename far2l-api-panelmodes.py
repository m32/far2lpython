#!/usr/bin/env vpython3
import sys
from far2l import PluginManager, pluginmanager as pm

sys.path.insert(1, 'plugins')

class Test:
    ffi = pm.ffi
    ffic = pm.ffic
    def f2s(self, s):
        return pm.ffi.string(s)

    def s2f(self, s):
        return pm.ffi.new("wchar_t []", s)

    def Test(self):
        py_pm_py_titles = [
            self.s2f("name"),
            self.s2f("type"),
            self.s2f("count"),
        ]
        py_pm_titles = self.ffi.new("wchar_t *[]", py_pm_py_titles)
        py_pm = [
            self.s2f("N,C0,C1"),    # ColumnTypes
            self.s2f("0,8,9"),      # ColumnWidths
            py_pm_titles,           # ColumnTitles
            0,                      # FullScreen
            0,                      # DetailedStatus
            0,                      # AlignExtensions
            0,                      # CaseConversion
            self.ffi.NULL,          # StatusColumnTypes
            self.ffi.NULL,          # StatusColumnWidths
            [0,0],                  # Reserved
        ]
        pm = self.ffi.new("struct PanelMode *", py_pm)

        wcn = self.ffi.cast("wchar_t *", self.ffi.NULL)
        py_kbt_normal = [wcn]*12
        py_kbt_ctrl = [wcn]*12
        py_kbt_alt = [wcn]*12
        py_kbt_ctrl_shift = [wcn]*12
        py_kbt_alt_shift = [wcn]*12
        py_kbt_ctrl_alt = [wcn]*12

        py_kbt_normal[4-1]=self.s2f("DDL")

        py_kbt = [
            py_kbt_normal,
            py_kbt_ctrl,
            py_kbt_alt,
            py_kbt_ctrl_shift,
            py_kbt_alt_shift,
            py_kbt_ctrl_alt
        ]

        kbt = self.ffi.new("struct KeyBarTitles *", py_kbt)

def main():
    cls = Test()
    cls.Test()

main()
