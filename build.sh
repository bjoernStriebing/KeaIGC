#!/usr/bin/env bash
PYTHONPATH=venv/lib/python2.7/site-packages

cd "$(dirname "$0")"
rm -rf build/*
rm igc/save.so

# compile and sign GPS device classes
rm gpsdevice/*.pyc gpsdevice/*.sig
python -m compileall gpsdevice/
python gpsdevice/_sign.py

# compile the igc signing library
python setup_igc_so.py build_ext
if [ $? -eq 0 ]; then
    gcc --shared -Ivenv/include/python2.7/ $(python-config --ldflags) build/igc/private/save.c -o igc/save.so
fi
