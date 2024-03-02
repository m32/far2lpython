FAR2L := ../far2l
VPYTHON := /devel/bin/python3/bin/python

PYCONFIG=python3.11-config

python_version_full := $(wordlist 2,4,$(subst ., ,$(shell $(VPYTHON) --version 2>&1)))
python_version_major := $(word 1,${python_version_full})
python_version_minor := $(word 2,${python_version_full})
python_version_patch := $(word 3,${python_version_full})
python_version = ${python_version_major}.${python_version_minor}

PYTHON_LIBRARY = /usr/lib/x86_64-linux-gnu/libpython3.11.so.1.0

CFLAGS += $(shell $(PYCONFIG) --cflags)
LDFLAGS += -g -lpython${python_version} $(shell $(PYCONFIG) --ldflags)

CFLAGS += \
	-g -Og \
    -DVIRTUAL_PYTHON=\"$(VPYTHON)\" \
    -DPYTHON_LIBRARY=\"$(PYTHON_LIBRARY)\" \
    -DWINPORT_DIRECT \
    -DUNICODE \
    -DFAR_USE_INTERNALS \
    -DPROCPLUGINMACROFUNC \
    -I . \
    -I $(FAR2L)/WinPort \
    -I $(FAR2L)/utils/include \
    -I $(FAR2L)/far2l/far2sdk

all : python.far-plug-wide far2lcffi.py.cpp

install : /devel/bin/farg/Plugins/python/plug/python.far-plug-wide
/devel/bin/farg/Plugins/python/plug/python.far-plug-wide : python.far-plug-wide
	cp $< $@

python.far-plug-wide : python.o
	g++ -fPIC -shared -o $@ $^ $(LDFLAGS)

python.o : python.cpp
	g++ -fPIC -o $@ -c $(CFLAGS) $^

consts.h : consts.gen
	cpp -E -P -xc consts.gen | sh > consts.h

far2lcffi.py.cpp: consts.h pythongen.py
	$(VPYTHON) pythongen.py $(FAR2L) .
	cp $@ far2l

clean:
	rm -f consts.h far2lcffi.py.cpp far2l/far2lcffi.py.cpp python.far-plug-wide python.o

xx.so : xx.cpp
	g++ -fPIC -shared -o $@ $(CFLAGS) $^

xx.i : xx.cpp
	g++ -E -fPIC -shared -o $@ $(CFLAGS) $^
