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

# version setup
VERSION=$(git describe --tags --long | \
          awk '{split($0,t,"-"); if (t[2] == 0) {print t[1]} else {print $0}}')

rm -rf build && mkdir build
rm -rf dist && mkdir dist

# compile and sign GPS device classes
rm gpsdevice/lib/*.so gpsdevice/lib/*.sig
cp "$PACKAGING_DIR/setup_gpsdevice.py" _setup_gpsdevice.py
python _setup_gpsdevice.py build_ext --inplace
python gpsdevice/_sign.py
mv gpsdevice/*.so gpsdevice/*.sig gpsdevice/lib/
rm _setup_gpsdevice.py*

if $SHAREDOBJ; then
    # compile the igc signing library
    rm igc/save*.so
    cp "$PACKAGING_DIR/setup_igc_so.py" _setup_igc_so.py
    python _setup_igc_so.py build_ext --inplace
    rm _setup_igc_so.py*
    if [ $? -eq 0 ]; then
        mv igc/_private/save.cpython-37m-darwin.so igc/
    fi
fi

# build the actual app
sed "s/'CFBundleShortVersionString': '.*'/'CFBundleShortVersionString': '$VERSION'/" \
    "$PACKAGING_DIR/keaigc.spec" > _keaigc.spec
pyinstaller \
    -y \
    --debug all \
    --onefile \
    --windowed \
    --distpath="dist" \
    --workpath="build" \
    _keaigc.spec
rm _keaigc.spec

if $DMGIMAGE; then
    # update installer
    rm packaging/Kea\ IGC\ Forager.dmg || true
    dmgbuild -s "packaging/osx_dmg_settings.py" \
      "Kea IGC Forager" \
      "dist/Kea IGC Forager.dmg"
    mv dist/Kea\ IGC\ Forager.dmg ~/Desktop/
fi
