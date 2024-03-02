#!/usr/bin/env vpython3
import os
import stat
import re
import logging
from datetime import datetime
from adbutils import AdbClient, AdbError

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
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

TICKSPERSEC        =10000000
TICKSPERMSEC       =10000
SECSPERDAY         =86400
SECSPERHOUR        =3600
SECSPERMIN         =60
MINSPERHOUR        =60
HOURSPERDAY        =24
EPOCHWEEKDAY       =1  #/* Jan 1, 1601 was Monday */
DAYSPERWEEK        =7
MONSPERYEAR        =12


class Entry:
    def __init__(self, dirname=None, perms=None, links=1, uid=0, gid=0, size=None,
                 date_time=None, date=None, name=None):
        """initialize file"""
        self.mode = 0
        self.perms = perms
        self.links = links
        self.uid = uid
        self.gid = gid
        self.size = int(size) if size else 0
        self.date_time = date_time
        self.name = name
        self.date = date

        self.dirname = dirname
        self.link_target = None
        self.filepath = os.path.join(self.dirname, self.name)
        self.perms2mode()

    def update(self, box):
        """update object fields"""
        month_num = {'Jan': 1,
                     'Feb': 2,
                     'Mar': 3,
                     'Apr': 4,
                     'May': 5,
                     'Jun': 6,
                     'Jul': 7,
                     'Aug': 8,
                     'Sep': 9,
                     'Oct': 10,
                     'Nov': 11,
                     'Dec': 12}
        if self.date_time:
            date = self.date_time.split()
            date = '%s-%02d-%s %s' % (date[1],
                                      month_num[date[0]],
                                      date[3],
                                      date[2])
            date = datetime.strptime(date, '%d-%m-%Y %H:%M:%S')
        else:
            date = datetime.strptime(self.date, box['date_re'])

        self.date = date
        self.date_time = date.strftime('%Y-%m-%d %H:%M')

        type = self.perms[0] if self.perms else None

        if type == 'l' and ' -> ' in self.name:
            self._correct_link()


    def perms2mode(self):
        perms = self.perms[1:]
        lperms = len(perms)
        mode = 0
        # Check if 'perms' has the right format
        if (
            not [x for x in perms if x not in '-rwxXsStT']
            and lperms == 9
        ) :
            pos = lperms - 1
            for c in perms:
                if c in 'sStT' :
                    # Special modes
                    mode += (1 << pos // 3) << 9

                mode += 1 << pos if c in 'rwxst' else 0
                pos -= 1
        self.mode = mode | {
            '-': 0,
            'b': stat.S_IFBLK,
            'c': stat.S_IFCHR,
            'd': stat.S_IFDIR,
            'l': stat.S_IFLNK,
            'p': 0, #stat.S_IF???,
            's': 0, #stat.S_IF???,
        }[self.perms[0]]

    def _correct_link(self):
        """Canonize filename and fill the link attr"""
        try:
            name, target = self.name.split(' -> ')
        except ValueError:
            return

        self.name = name

        if not self.size:
            self.size = 0

        if target.startswith('/'):
            self.link_target = target
        else:
            self.link_target = os.path.abspath(os.path.join(self.dirname, target))
        self.filepath = os.path.join(self.dirname, self.name)

    def mk_link_relative(self):
        """Convert links to relative"""
        self.link_target = os.path.relpath(self.link_target, self.dirname)

    def __str__(self):
        if not self.name:
            return ''

        template = ('{mode:4o} {perms} {links:>4} {uid:<8} {gid:<8} {size:>8} {date} {name}')
        return template.format(**self.__dict__)

class Shell:
    boxes = {
        'busybox': {
            'ls': 'busybox ls -anL --full-time {}',
            'rls': 'busybox ls -Ranl {}',
            'date_re': '%Y-%m-%d %H:%M:%S %z',
            'file_re':
                r'^'
                r'(?P<perms>[-bcdlps][-rwxsStT]{9})\s+'
                r'(?P<links>\d+)\s'
                r'(?P<uid>\d+)\s+'
                r'(?P<gid>\d+)\s+'
                r'(?P<size>\d+)\s'
                r'(?P<date>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\+\d{4})\s'
                r'(?P<name>.*)',
        },
        'toolbox': {
            'ls': 'ls -anl {}',
            'rls': 'ls -Ranl {}',
            'date_re': '%Y-%m-%d %H:%M',
            'file_re':
                r'^(?P<perms>[-bcdlps][-rwxsStT]{9})\s+'
                r'(?P<links>\d+)\s'
                r'(?P<uid>\d+)\s+'
                r'(?P<gid>\d+)\s+'
                r'(?P<size>\d+)?\s'
                r'(?P<date>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})\s'
                r'(?P<name>.*)',
        },
        'toybox': {
            'ls': 'toybox ls -anLc {}',
            'rls':  'toybox ls -Ranl {}',
            'date_re': '%Y-%m-%d %H:%M',
            'file_re':
                r'^(?P<perms>[-bcdlps][-rwxsStT]{9})\s+'
                r'(?P<links>\d+)\s+'
                r'(?P<uid>\d+)\s+'
                r'(?P<gid>\d+)\s+'
                r'(?P<size>\d+)?\s'
                r'(?P<date>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})\s'
                r'(?P<name>.*)',
        }
    }
    def __init__(self, dev):
        box = None
        for name in (
#            'busybox',
#            'toolbox',
            'toybox',
        ):
            line = dev.shell('which '+name).strip()
            if line:
                box = name
                break
        else:
            raise IOError(2, 'unknown shell')
        self.box = self.boxes[box]
        self.file_re = re.compile(self.box['file_re'])

    def list(self, dev, top):
        dtop = top
        if dtop[-1] != '/':
            dtop += '/'
        cmd = self.box['ls'].format(dtop)
        lines = dev.shell(cmd)
        result = []
        for line in lines.split('\n'):
            line = line.strip()
            if not line:
                continue
            rm = self.file_re.match(line)
            if not rm:
                log.debug('ignored entry in ({}): {}'.format(top, line))
                continue
            entry = Entry(top, **rm.groupdict())
            entry.update(self.box)
            if entry.perms[0] == 'l':
                self.listfix(dev, entry, entry.link_target)
            result.append(entry)
        return result

    def listfix(self, dev, entry, target):
        lines = dev.shell('stat '+target).split('\n')
        target = lines[0].split(' -> ')
        if len(target) == 2:
            target = target[1].strip()[1:-1]
            return self.listfix(dev, entry, target)
        try:
            perms = lines[3].split(')')[0]
            perms = perms.split('(')[1]
            perms = perms.split('/')[1]
            if perms[0] != 'd':
                entry.size = int(lines[1].split()[1])
            entry.perms = perms
            entry.perms2mode()
        except IndexError:
            # link to non existing element
            pass

clt = AdbClient()
device = clt.device_list()[0]
shell = Shell(device)
result = shell.list(device, '/bin')
for rec in result:
    print(rec)
