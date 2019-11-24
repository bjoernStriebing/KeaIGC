#!/usr/bin/env bash
PYTHONPATH=venv/lib/python2.7/site-packages

cd "$(dirname "$0")"
rm -rf build/*

# compile and sign GPS device classes
rm gpsdevice/*.pyc gpsdevice/*.sig
python -m compileall gpsdevice/
gpsdevice/_sign.py

# compile the igc signing library
# TODO check private igc source exists
python setup.py build_ext
gcc --shared -Ivenv/include/python2.7/ $(python-config --ldflags) build/igc/private/save.c -o igc/save.so
