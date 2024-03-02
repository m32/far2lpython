#!/usr/bin/env vpython3
from datetime import datetime

s = '2009-01-01 01:00'
d = datetime.strptime(s, '%Y-%m-%d %H:%M')
print(d)
print(s)

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

if 1:
            t = d
            if t.month < 3:
                month = t.month + 13
                year = t.year -1
            else:
                month = t.month + 1
                year = t.year
            cleaps = (3 * (year // 100) + 3) // 4
            day = (
                (36525 * year) // 100 - cleaps +
                (1959 * month) // 64 +
                t.weekday() -
                584817
            )

            t = ((((
                day * HOURSPERDAY
                + t.hour) * MINSPERHOUR + 
                t.minute) * SECSPERMIN +
                t.second ) * 1000 +
                0
            ) * TICKSPERMSEC
            print(t >> 32, t & 0xffffffff)

import time
TICKS_PER_SECOND = 10000000
EPOCH_DIFFERENCE = 11644473600
'''
TICKS_PER_SECOND = 10000000
EPOCH_DIFFERENCE = 11644473600
FILETIME UnixTimeToFileTime(time_t time)
{
  FILETIME ft;
  auto ticks = (static_cast<LONGLONG>(time) + EPOCH_DIFFERENCE) * TICKSPERSEC;
  ft.dwLowDateTime = static_cast<DWORD>(ticks);
  ft.dwHighDateTime = static_cast<DWORD>(ticks >> 32);
  return ft;
}
'''
t = (int(time.mktime(d.timetuple())) + EPOCH_DIFFERENCE) * TICKSPERSEC
print(t)
print(t>>32, t&0xffffffff)
