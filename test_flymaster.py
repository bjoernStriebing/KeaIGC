#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from gpsdevice import gpsflymaster


if __name__ == '__main__':
    gps = gpsflymaster.GpsFlymaster(sys.argv[1])
    gps.set_nav_off()
    gps.get_id()
    gps.get_list()
    if len(sys.argv) > 2:
        gps.get_flight(sys.argv[2])
