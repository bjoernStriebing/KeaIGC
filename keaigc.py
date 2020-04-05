#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import argparse

sys.path.append(os.path.dirname(__file__))
logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download IGC files from GPS Devices.')
    parser.add_argument('--dev', '--developer', dest='dev', action='store_true',
                        help="Use GPS device class source not compiled library\n\
                              Downloaded IGC files won't be signed.")
    parser.add_argument('--cmd', dest='cmd', action='store_true',
                        help="Don't show the GUI - use command line interface.")
    parser.add_argument('-g', '--gps', dest='gps', type=str,
                        metavar='class', default='<NOT SET>',
                        help="GPS device class")
    parser.add_argument('-s', '--serial', dest='serial', type=str,
                        metavar='path', default='<NOT SET>',
                        help="Serial port device path")
    parser.add_argument('-f', '--flights', dest='flights', type=int,
                        metavar='N', default=None, nargs='+',
                        help="Serial port device path")
    parser.add_argument('--pilot', dest='pilot', type=str,
                        metavar='name', default=None, nargs='+',
                        help="Pilot name to place in IGC metadata")
    parser.add_argument('--glider', dest='glider', type=str,
                        metavar='name', default=None, nargs='+',
                        help='Glider Brand and Model in to place in IGC metadata')
    parser.add_argument('-o', '--out', dest='out', type=str,
                        metavar='dir', default='~/Desktop',
                        help="Output folder")
    args, unknown = parser.parse_known_args()
    sys.argv[1:] = unknown

    import gpsdevice
    gpsdevice.import_lib(developer=args.dev)

    if not args.cmd:
        """Run the GUI app"""
        from gui.keaigcapp import KeaIgcApp
        from packaging.autoupdate import KeaIgcUpdate
        app = KeaIgcApp()
        autoupdate = KeaIgcUpdate(app)
        app.run()

    else:
        """Run the CMD app"""
        import keaigccmd
        keaigccmd.run(args)
