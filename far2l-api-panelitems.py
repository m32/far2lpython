#!/usr/bin/env vpython3
import sys
import gc

from far2l import PluginManager, pluginmanager as pm

sys.path.insert(1, 'plugins')

class Test:
    ffi = pm.ffi
    ffic = pm.ffic
    def f2s(self, s):
        return pm.ffi.string(s)

    def s2f(self, s):
        return pm.ffi.new("wchar_t []", s)

    def GetFindData(self):
        recs = [
            ('view', 'customer', 1),
            ('table', 'user', 2),
        ]
        names = []
        names1 = []
        items = self.ffi.new("struct PluginPanelItem []", len(recs))
        for no in range(len(recs)):
            rec = recs[no]
            names.append(self.s2f(rec[0])) # type
            items[no].FindData.lpwszFileName = names[-1]
            names.append(str(rec[2]))
            names.append([self.s2f(rec[1]), self.s2f(names[-1])]) # name, size
            names.append(self.ffi.new("wchar_t *[]", names[-1]))
            items[no].CustomColumnData = names[-1]
            items[no].CustomColumnNumber = 2
        self.recs = recs
        self.names = names
        self.names1 = names1
        return items

    def FreeFindData(self, items):
        print('FreeFindData')
        for item in items:
            item.FindData.lpwszFileName = self.ffi.NULL
            item.CustomColumnData = self.ffi.NULL
        self.names1 = None
        self.names = None
        self.recs = None

def main():
    cls = Test()
    try:
        i = cls.GetFindData()
        gc.collect()
        s = i[0].FindData.lpwszFileName
        print('ptr:{} val:{} cols:{}'.format(s, pm.ffi.string(s), i[0].CustomColumnNumber))
        for no in range(i[0].CustomColumnNumber):
            s = i[0].CustomColumnData[no]
            print('\tno:{} ptr:{} val:{}'.format(no, s, pm.ffi.string(s)))
        cls.FreeFindData(i)
        del i
        print('collect')
        gc.collect()
    except:
        import traceback
        traceback.print_exc()
main()
