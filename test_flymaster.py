#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from serial.serialutil import SerialException
sys.path.append(os.path.dirname(__file__))

from igc import save as igc_save                                        # nopep8
from gpsdevice import gpsflymaster                                      # nopep8


if __name__ == '__main__':
    try:
        gps = gpsflymaster.GpsFlymaster(sys.argv[1])
    except SerialException as e:
        # TODO logging
        print e
        exit(1)
    gps.set_nav_off()
    gps.get_id()
    gps.get_list()
    if len(sys.argv) > 2:
        try:
            print igc_save.download(gps, sys.argv[2])
        except igc_save.UnsignedIGCException as e:
            print e
            exit(1)

        # print ','.join(['num', 'latitude', 'longitude', 'altitude'])
        # for i, fix in enumerate(tracklog):
        #     print ','.join(map(str, [i, fix.latitude, fix.longitude, fix.altitude_gps]))
