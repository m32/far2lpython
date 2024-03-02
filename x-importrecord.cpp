#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string>
#include <dlfcn.h>

#if !defined(__APPLE__) && !defined(__FreeBSD__) && !defined(__DragonFly__)
# include <alloca.h>
#endif

#include <Python.h>

#include <windows.h>
#include <Threaded.h>
#include <utils.h>

#include <farplug-wide.h>
#include <farcolor.h>
#include <farkeys.h>

static INPUT_RECORD rec;

extern "C" INPUT_RECORD *getrec()
{
    return &rec;
}

extern "C" void decode()
{
    printf("sizeof=%ld\n", sizeof(INPUT_RECORD));
    printf("rec=%p\n", &rec);
    printf("EventType=%d\n", rec.EventType);
    printf("bKeyDown=%04X\n", rec.Event.KeyEvent.bKeyDown);
    printf("wVirtualKeyCode=%04X\n", rec.Event.KeyEvent.wVirtualKeyCode);
    printf("dwControlKeyState=%08X\n", rec.Event.KeyEvent.dwControlKeyState);
}

extern "C" void encode()
{
    rec.EventType=1;
    rec.Event.KeyEvent.bKeyDown = 0x4321;
    rec.Event.KeyEvent.wRepeatCount = 1;
    rec.Event.KeyEvent.wVirtualKeyCode = 0x1234;
    rec.Event.KeyEvent.dwControlKeyState = 0x5a5a5a5a;
}
