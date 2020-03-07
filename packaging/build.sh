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
rm -rf dist && mkdir dist

# compile and sign GPS device classes
mv gpsdevice/lib/*.so gpsdevice/lib/*.sig
cp "$PACKAGING_DIR/setup_gpsdevice.py" _setup_gpsdevice.py
python _setup_gpsdevice.py build_ext --inplace
python gpsdevice/_sign.py
mv gpsdevice/*.so gpsdevice/*.sig gpsdevice/lib/
rm _setup_gpsdevice.py*

if $SHAREDOBJ; then
    # compile the igc signing library
    rm igc/save.so
    cp "$PACKAGING_DIR/setup_igc_so.py" _setup_igc_so.py
    python _setup_igc_so.py build_ext --inplace
    rm _setup_igc_so.py*
    if [ $? -eq 0 ]; then
        mv igc/_private/save.so igc/save.so
    fi
fi

# mv igc/_private igc/__private

# build the actual app
cp "$PACKAGING_DIR/keagps.spec" _keagps.spec
pyinstaller \
    -y \
    --debug all \
    --distpath="dist" \
    --workpath="build" \
    _keagps.spec
rm _keagps.spec
# mv igc/__private igc/_private

if $DMGIMAGE; then
    # update installer
    true
fi
