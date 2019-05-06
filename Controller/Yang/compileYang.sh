#!/bin/bash
export PYBINDPLUGIN=`/usr/bin/env python -c \
        'import pyangbind; import os; print "%s/plugin" % os.path.dirname(pyangbind.__file__)'`
pyang --plugindir $PYBINDPLUGIN -f pybind normalBehaviour.yang > normalBehaviour.py
