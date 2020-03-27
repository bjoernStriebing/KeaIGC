#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import argparse
from serial.serialutil import SerialException
sys.path.append(os.path.dirname(__file__))
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from igc import save as igc_save                                        # nopep8
from gpsdevice import gpsflymaster                                      # nopep8


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download IGC files from GPS Devices.')
    from gui.keagpsapp import KeaGpsApp
    app = KeaGpsApp()
    app.run()
    # try:
    #     gps = gpsflymaster.GpsFlymaster(sys.argv[1])
    # except SerialException as e:
    #     logger.critical(e)
    #     sys.exit(1)
    # gps.set_nav_off()
    # gps.get_id()
    # gps.get_list()
    # if len(sys.argv) > 2:
    #     try:
    #         print igc_save.download(gps, sys.argv[2])
    #     except igc_save.UnsignedIGCException as e:
    #         print e, '\n'
    #         sys.exit(1)
