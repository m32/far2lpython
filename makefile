FAR2L := ../far2l
VPYTHON := /devel/bin/python3/bin/python

PYCONFIG=python3-config

python_version_full := $(wordlist 2,4,$(subst ., ,$(shell $(VPYTHON) --version 2>&1)))
python_version_major := $(word 1,${python_version_full})
python_version_minor := $(word 2,${python_version_full})
python_version_patch := $(word 3,${python_version_full})
python_version = ${python_version_major}.${python_version_minor}

PYTHON_LIBRARY = $(shell $(PYCONFIG) --configdir)/libpython${python_version}.so

CFLAGS += $(shell $(PYCONFIG) --cflags)
LDFLAGS += -lpython${python_version} $(shell $(PYCONFIG) --ldflags)

CFLAGS += \
    -DVIRTUAL_PYTHON_PATH=L\"$(VPYTHON)\" \
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

python.far-plug-wide : python.o
	g++ -fPIC -shared -o $@ $^ $(LDFLAGS)

python.o : python.cpp
	g++ -fPIC -o $@ -c $(CFLAGS) $^

consts.h : consts.gen
	cpp -E -P -xc consts.gen | sh > consts.h

far2lcffi.py.cpp: consts.h pythongen.py
	$(VPYTHON) pythongen.py $(FAR2L)
	cp $@ far2l

clean:
	rm -f consts.h far2lcffi.py python.far-plug-wide python.o
