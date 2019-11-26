#!/usr/bin/env bash
PACKAGING_DIR="$(dirname $0)"
PYTHONPATH=venv/lib/python2.7/site-packages
SHAREDOBJ=false
DMGIMAGE=false
for i in "$@"; do
    case $i in
        (--so) SHAREDOBJ=true; shift;;
        (--dmg) DMGIMAGE=true; shift;;
        (*) ;;
    esac
done

rm -rf build && mkdir build
cd "$PACKAGING_DIR"

# compile and sign GPS device classes
rm ../gpsdevice/*.pyc ../gpsdevice/*.sig
python -m compileall ../gpsdevice/
python ../gpsdevice/_sign.py

if $SHAREDOBJ; then
    # compile the igc signing library
    cd ..
    rm igc/save.so
    cp "$PACKAGING_DIR/setup_igc_so.py" _setup_igc_so.py
    python _setup_igc_so.py build_ext --inplace
    rm _setup_igc_so.py*
    if [ $? -eq 0 ]; then
        mv igc/private/save.so igc/save.so
    fi
    cd "$PACKAGING_DIR"
fi

# build the actual app
pyinstaller \
    -y \
    --debug all \
    --distpath="../dist" \
    --workpath="../build" \
    keagps.spec

if $DMGIMAGE; then
    # update installer
    true
fi
