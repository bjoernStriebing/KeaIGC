#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(__file__))

from igc import save as igc_save
from gpsdevice import gpsflymaster


if __name__ == '__main__':
    gps = gpsflymaster.GpsFlymaster(sys.argv[1])
    # TODO: WIP disabled for faster testing
    # gps.set_nav_off()
    # gps.get_id()
    # gps.get_list()
    if len(sys.argv) > 2:
        print igc_save.download(gps, sys.argv[2])

        # print ','.join(['num', 'latitude', 'longitude', 'altitude'])
        # for i, fix in enumerate(tracklog):
        #     print ','.join(map(str, [i, fix.latitude, fix.longitude, fix.altitude_gps]))
