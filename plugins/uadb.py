import os
import stat
import logging
from far2l.plugin import PluginVFS
from far2l.fardialogbuilder import (
    Spacer,
    TEXT, EDIT, PASSWORD, MASKED, MEMOEDIT,
    BUTTON, CHECKBOX, RADIOBUTTON, COMBOBOX,
    LISTBOX, USERCONTROL,
    HLine,
    HSizer, VSizer,
    DialogBuilder
)

import stat
import datetime
from adbutils import AdbClient, AdbError

log = logging.getLogger(__name__)

FILE_ATTRIBUTE_READONLY             =0x00000001
FILE_ATTRIBUTE_HIDDEN               =0x00000002
FILE_ATTRIBUTE_SYSTEM               =0x00000004
FILE_ATTRIBUTE_DIRECTORY            =0x00000010
FILE_ATTRIBUTE_ARCHIVE              =0x00000020
FILE_ATTRIBUTE_DEVICE               =0x00000040
FILE_ATTRIBUTE_NORMAL               =0x00000080
FILE_ATTRIBUTE_TEMPORARY            =0x00000100
FILE_ATTRIBUTE_SPARSE_FILE          =0x00000200
FILE_ATTRIBUTE_REPARSE_POINT        =0x00000400
FILE_ATTRIBUTE_COMPRESSED           =0x00000800
FILE_ATTRIBUTE_OFFLINE              =0x00001000
FILE_ATTRIBUTE_NOT_CONTENT_INDEXED  =0x00002000
FILE_ATTRIBUTE_ENCRYPTED            =0x00004000
FILE_ATTRIBUTE_INTEGRITY_STREAM     =0x00008000
FILE_ATTRIBUTE_VIRTUAL              =0x00010000
FILE_ATTRIBUTE_NO_SCRUB_DATA        =0x00020000
FILE_ATTRIBUTE_BROKEN               =0x00200000
FILE_ATTRIBUTE_EXECUTABLE           =0x00400000

class Plugin(PluginVFS):
    label = "Python ADB"
    openFrom = ["PLUGINSMENU", "DISKMENU"]

    def OpenPlugin(self, OpenFrom):
        self.names = []
        self.Items = []
        self.clt = AdbClient()
        self.deviceserial = None
        self.device = None
        self.devicepath = '/'
        return True

    def loadDevices(self):
        for d in self.clt.list():
            self.addName(d.serial, FILE_ATTRIBUTE_DIRECTORY, 0)

    def setName(self, i, name, attr, size):
        self.names[i] = self.s2f(name)
        item = self.Items[i].FindData
        item.dwFileAttributes = attr
        item.nPhysicalSize = size
        item.nFileSize = size
        item.lpwszFileName = self.names[i]

    def addName(self, name, attr, size):
        #log.debug('addName({})'.format(name))
        # increase C array
        items = self.ffi.new("struct PluginPanelItem []", len(self.Items)+1)
        for i in range(len(self.Items)):
            items[i] = self.Items[i]
        self.Items = items
        self.names.append(None)
        self.setName(len(self.Items)-1, name, attr, size)

    def addResult(self, result):
        n = 0
        for rec in result:
            if rec.path in ('.', '..'):
                continue
            n += 1
        self.Items = self.ffi.new("struct PluginPanelItem []", n)
        self.names = [None]*n
        i = 0
        for rec in result:
            if rec.path in ('.', '..'):
                continue
            mode = stat.filemode(rec.mode)
            if mode[0] == 'd':
                attr = FILE_ATTRIBUTE_DIRECTORY
            else:
                attr = FILE_ATTRIBUTE_ARCHIVE
            #datetime.datetime.fromtimestamp(rec.time).strftime('%Y-%m-%d %H:%M:%S')
            self.setName(i, rec.path, attr, rec.size)
            i += 1

    def deleteNames(self, names):
        found = []
        for i in range(len(self.names)):
            if self.f2s(self.names[i]) in names:
                found.append(i)
        if len(found) == 0:
            return False
        # new array
        n = len(self.Items)-len(found)
        if n > 0:
            items = self.ffi.new("struct PluginPanelItem []", n)
            j = 0
            for i in range(len(self.Items)):
                if i not in found:
                    items[j] = self.Items[i]
                    j += 1
            # delete
            for i in sorted(found, reverse=True):
                del self.names[i]
        else:
            self.names = []
            items = []
        self.Items = items
        self.info.Control(self.hplugin, self.ffic.FCTL_UPDATEPANEL, 0, 0)
        self.info.Control(self.hplugin, self.ffic.FCTL_REDRAWPANEL, 0, 0)
        return True

    def Message(self, lines):
        _MsgItems = [
            self.s2f('ADB'),
            self.s2f(''),
        ]
        for line in lines:
            _MsgItems.append(
                self.s2f(line)
            )
        _MsgItems.extend([
            self.s2f(""),
            self.s2f("\x01"),
            self.s2f("&Ok"),
        ])
        #log.debug('_msgItems: %s', _MsgItems)
        MsgItems = self.ffi.new("wchar_t *[]", _MsgItems)
        self.info.Message(
            self.info.ModuleNumber,                             # GUID
            self.ffic.FMSG_WARNING|self.ffic.FMSG_LEFTALIGN,    # Flags
            self.s2f("Contents"),                               # HelpTopic
            MsgItems,                                           # Items
            len(MsgItems),                                      # ItemsNumber
            1                                                   # ButtonsNumber
        )

    def ConfirmDialog(self, title, lines):
        _MsgItems = [
            self.s2f(title),
            self.s2f(''),
        ]
        for line in lines:
            _MsgItems.append(
                self.s2f(line)
            )
        _MsgItems.extend([
            self.s2f(""),
            self.s2f("\x01"),
            self.s2f("&Cancel"),
            self.s2f("&Ok"),
        ])
        #log.debug('_msgItems: %s', _MsgItems)
        MsgItems = self.ffi.new("wchar_t *[]", _MsgItems)
        rc = self.info.Message(
            self.info.ModuleNumber,                             # GUID
            self.ffic.FMSG_WARNING|self.ffic.FMSG_LEFTALIGN,    # Flags
            self.s2f("Contents"),                               # HelpTopic
            MsgItems,                                           # Items
            len(MsgItems),                                      # ItemsNumber
            2                                                   # ButtonsNumber
        )
        # 0 = Cancel, 1 = OK
        #log.debug('confirm={}'.format(rc))
        return rc

    def GetOpenPluginInfo(self, OpenInfo):
        Info = self.ffi.cast("struct OpenPluginInfo *", OpenInfo)
        Info.Flags = (
            self.ffic.OPIF_USEFILTER
            |self.ffic.OPIF_USESORTGROUPS
            |self.ffic.OPIF_USEHIGHLIGHTING
            |self.ffic.OPIF_ADDDOTS
            |self.ffic.OPIF_SHOWNAMESONLY
        )
        Info.HostFile = self.ffi.NULL
        Info.CurDir = self.s2f(self.devicepath)
        if self.device is not None:
            title = "adb://{}{}".format(self.device.serial, self.devicepath)
        else:
            title = self.label
        Info.Format = self.s2f(self.label)
        Info.PanelTitle = self.s2f(" *"+title+"* ")
        #const struct InfoPanelLine *InfoLines;
        #int                   InfoLinesNumber;
        #const wchar_t * const   *DescrFiles;
        #int                   DescrFilesNumber;
        #const struct PanelMode *PanelModesArray;
        Info.PanelModesNumber = 0
        Info.StartPanelMode = 0
        #Info.StartSortMode = self.ffic.SM_NAME
        #Info.StartSortOrder = 0
        #const struct KeyBarTitles *KeyBar;
        Info.ShortcutData = self.s2f('py:adb cd '+title)

    def GetFindData(self, PanelItem, ItemsNumber, OpMode):
        #super().GetFindData(PanelItem, ItemsNumber, OpMode)
        if self.device is None:
            try:
                self.loadDevices()
            except RuntimeError as why:
                log.error(why)
                lines=str(why).split('\n')
                lines.insert(0, 'RuntimeError:')
                self.Message(lines)
                return False
            except AdbError as ex:
                log.exception('AdbError')
                self.Message(str(ex).split('\n'))
                return False
            except Exception as ex:
                log.exception('unknown exception:')
                msg = str(ex).split('\n')
                msg.insert(0, 'Unknown exception.')
                self.Message(msg)
                return False
        else:
            try:
                result = self.device.sync.list(self.devicepath)
                self.addResult(result)
            except AdbError as ex:
                log.exception('AdbError')
                self.Message(str(ex).split('\n'))
                return False
            except Exception as ex:
                log.exception('unknown exception:')
                msg = str(ex).split('\n')
                msg.insert(0, 'Unknown exception.')
                self.Message(msg)
                return False
        PanelItem = self.ffi.cast('struct PluginPanelItem **', PanelItem)
        ItemsNumber = self.ffi.cast('int *', ItemsNumber)
        n = len(self.Items)
        p = self.ffi.NULL if n == 0 else self.Items
        PanelItem[0] = p
        ItemsNumber[0] = n
        #log.debug("ADB.GetFindData, p={} n={}".format(p, n))
        return True

    def FreeFindData(self, PanelItem, ItemsNumber):
        #log.debug("ADB.FreeFindData({0}, {1}, n.names={2}, n.Items={3})".format(PanelItem, ItemsNumber, len(self.names), len(self.Items)))
        self.names = []
        self.Items = []

    def SetDirectory(self, Dir, OpMode):
        #super().SetDirectory(Dir, OpMode)
        #if OpMode & self.ffic.OPM_FIND:
        #    return False
        name = self.f2s(Dir)
        #log.debug('goto.0: devicepath={} name={}'.format(self.devicepath, name))
        if name == "":
            self.info.Control(self.hplugin, self.ffic.FCTL_CLOSEPLUGIN, 0, 0)
            return True
        #log.debug('goto.1: devicepath={} name={}'.format(self.devicepath, name))
        if name == "..":
            if self.device is None:
                self.info.Control(self.hplugin, self.ffic.FCTL_CLOSEPLUGIN, 0, Dir)
                return True
            if self.devicepath == '/':
                self.device = None
            else:
                self.devicepath = os.path.normpath(os.path.join(self.devicepath, name))
            #log.debug('goto.2: devicepath={}'.format(self.devicepath))
        elif self.device is None:
            try:
                self.device = self.clt.device(name)
                self.devicepath = '/'
                try:
                    self.device.root()
                    #log.debug('goto.3: rooted')
                except:
                    #log.debug('goto.3: not rooted')
                    pass
            except AdbError as ex:
                self.device = None
                log.exception('AdbError')
                self.Message(str(ex).split('\n'))
                return False
            except Exception as ex:
                self.device = None
                log.exception('unknown exception:')
                msg = str(ex).split('\n')
                msg.insert(0, 'Unknown exception.')
                self.Message(msg)
                return False
        else:
            self.devicepath = os.path.join(self.devicepath, name)
        return True

    def Compare(self, PanelItem1, PanelItem2, Mode):
        def cmp(a, b):
            if a < b:
                return -1
            elif a == b:
                return 0
            return 1
        p1 = self.ffi.cast('struct PluginPanelItem *', PanelItem1)
        p2 = self.ffi.cast('struct PluginPanelItem *', PanelItem2)
        n1 = self.f2s(p1.FindData.lpwszFileName)
        n2 = self.f2s(p2.FindData.lpwszFileName)
        rc = cmp(n1, n2)
        #log.debug('Compare: cmp({}, {})={}, mode={}'.format(n1, n2, rc, Mode))
        return rc

    def GetVirtualFindData(self, PanelItem, ItemsNumber, Path):
        return False

    def FreeVirtualFindData(self, PanelItem, ItemsNumber):
        log.debug('FreeVirtualFindData: {}, {}'.format(PanelItem, ItemsNumber))

    def ProcessEvent(self, Event, Param):
        #if Event == self.ffic.FE_IDLE:
        pass

    def GetFiles(self, PanelItem, ItemsNumber, Move, DestPath, OpMode):
        #super().GetFiles(PanelItem, ItemsNumber, Move, DestPath, OpMode)
        if ItemsNumber == 0 or Move:
            return False
        if self.device is None:
            self.Message(['GetFiles allowed only inside device.'])
            return True
        # TODO dialog with copy parameters
        # TODO progress dialog
        items = self.ffi.cast('struct PluginPanelItem *', PanelItem)
        DestPath = self.ffi.cast("wchar_t **", DestPath)
        dpath = self.ffi.string(DestPath[0])
        #log.debug('GetFiles: {} {} OpMode={}'.format(ItemsNumber, OpMode, dpath))
        for i in range(ItemsNumber):
            name = self.f2s(items[i].FindData.lpwszFileName)
            if name in ('.', '..'):
                continue
            sqname = os.path.join(self.devicepath, name)
            dqname = os.path.join(dpath, name)
            log.debug('pull: {} -> {} OpMode={}'.format(sqname, dqname, OpMode))
            try:
                self.device.sync.pull(sqname, dqname)
            except AdbError as ex:
                log.exception('AdbError')
                self.Message(str(ex).split('\n'))
                return False
            except Exception as ex:
                log.exception('unknown exception:')
                msg = str(ex).split('\n')
                msg.insert(0, 'Unknown exception.')
                self.Message(msg)
                return False
        return True

    def PutFiles(self, PanelItem, ItemsNumber, Move, SrcPath, OpMode):
        #super().PutFiles(PanelItem, ItemsNumber, Move, SrcPath, OpMode)
        if ItemsNumber == 0 or Move:
            return False
        if self.device is None:
            self.Message(['PetFiles allowed only inside device.'])
            return True
        items = self.ffi.cast('struct PluginPanelItem *', PanelItem)
        spath = self.f2s(SrcPath)
        for i in range(ItemsNumber):
            name = self.f2s(items[i].FindData.lpwszFileName)
            if name in ('.', '..'):
                continue
            sqname = os.path.join(spath, name)
            dqname = os.path.join(self.devicepath, name)
            #log.debug('push: {} -> {} OpMode={}'.format(sqname, dqname, OpMode))
            try:
                self.device.sync.push(sqname, dqname)
            except AdbError as ex:
                log.exception('AdbError')
                self.Message(str(ex).split('\n'))
                return False
            except Exception as ex:
                log.exception('unknown exception:')
                msg = str(ex).split('\n')
                msg.insert(0, 'Unknown exception.')
                self.Message(msg)
                return False
        return True

    def DeleteFiles(self, PanelItem, ItemsNumber, OpMode):
        #super().DeleteFiles(PanelItem, ItemsNumber, OpMode)
        if ItemsNumber == 0:
            return False
        if self.device is None:
            self.Message(['DeleteFiles allowed only inside device.'])
            return True
        items = self.ffi.cast('struct PluginPanelItem *', PanelItem)
        if ItemsNumber > 1:
            rc = self.ConfirmDialog('Delete', ['Do you wish to delete the files'])
        else:
            name = self.f2s(items[0].FindData.lpwszFileName)
            rc = self.ConfirmDialog('Delete', ['Do you wish to delete the file', name])
        if rc != 1:
            return True
        for i in range(ItemsNumber):
            name = self.f2s(items[i].FindData.lpwszFileName)
            if name in ('.', '..'):
                continue
            dqname = os.path.join(self.devicepath, name)
            log.debug('remove: {}, OpMode={}'.format(dqname, OpMode))
            try:
                st = self.device.sync.stat(dqname)
                if stat.S_ISDIR(st.mode):
                    s = self.device.shell('rmdir '+dqname)
                else:
                    s = self.device.shell('rm '+dqname)
                if s:
                    log.debug('result:'+s)
                    self.Message(s.split('\n'))
            except AdbError as ex:
                log.exception('AdbError')
                self.Message(str(ex).split('\n'))
                return False
            except Exception as ex:
                log.exception('unknown exception:')
                msg = str(ex).split('\n')
                msg.insert(0, 'Unknown exception.')
                self.Message(msg)
                return False
        return True

    def MakeDirectory(self, Name, OpMode):
        #super().DMakeDirectory(Name, OpMode)
        if self.device is None:
            self.Message(['Make directory allowed only inside device.'])
            return True
        name = self.ffi.cast("wchar_t **", Name)
        name = self.ffi.string(name[0])

        @self.ffi.callback("FARWINDOWPROC")
        def DialogProc(hDlg, Msg, Param1, Param2):
            if Msg == self.ffic.DN_INITDIALOG:
                log.debug('INITDIALOG')
                try:
                    dlg.SetText(dlg.ID_path, name)
                    dlg.SetFocus(dlg.ID_path)
                except:
                    log.exception('bang')
                log.debug('/INITDIALOG')
            elif Msg == self.ffic.DN_BTNCLICK:
                pass
            elif Msg == self.ffic.DN_KEY:
                if Param2 == self.ffic.KEY_ESC:
                    return 0
                if Param2 == self.ffic.KEY_LEFT:
                    pass
                elif Param2 == self.ffic.KEY_UP:
                    pass
                elif Param2 == self.ffic.KEY_RIGHT:
                    pass
                elif Param2 == self.ffic.KEY_DOWN:
                    pass
                elif Param2 == self.ffic.KEY_ENTER:
                    pass
                elif Param2 == self.ffic.KEY_ESC:
                    pass
            elif Msg == self.ffic.DN_MOUSECLICK:
                pass
            return self.info.DefDlgProc(hDlg, Msg, Param1, Param2)

        b = DialogBuilder(
            self,
            DialogProc,
            "Make folder",
            "makefolder",
            0,
            VSizer(
                TEXT("Create the &folder"),
                EDIT("path", 36, 40),
                HLine(),
                HSizer(
                    BUTTON('OK', "OK", True, flags=self.ffic.DIF_CENTERGROUP),
                    BUTTON('CANCEL', "Cancel", flags=self.ffic.DIF_CENTERGROUP),
                ),
            ),
        )
        dlg = b.build(-1, -1)

        res = self.info.DialogRun(dlg.hDlg)
        if res == dlg.ID_OK:
            path = dlg.GetText(dlg.ID_path).strip()
            path = os.path.normpath(os.path.join(self.devicepath, path))
            log.debug('mkdir {}'.format(path))
            if path:
                try:
                    s = self.device.shell('mkdir '+path)
                    if s:
                        log.debug('result:'+s)
                        self.Message(s.split('\n'))
                except AdbError as ex:
                    log.exception('AdbError')
                    self.Message(str(ex).split('\n'))
                    return False
                except Exception as ex:
                    log.exception('unknown exception:')
                    msg = str(ex).split('\n')
                    msg.insert(0, 'Unknown exception.')
                    self.Message(msg)
                    return False
        self.info.DialogFree(dlg.hDlg)

        return True

    def ProcessKey(self, Key, ControlState):
        #log.debug("ProcessKey({0}, {1})".format(Key, ControlState))
        return 0
