import os
import sys

__all__ = ['GpsDevices']

GpsDevices = []


def import_lib(developer=False):
    global GpsDevices
    global gpsmisc
    global gpsbase
    global gpsflymaster

    frozen = getattr(sys, 'frozen', False)
    if frozen:
        import lib.gpsmisc as gpsmisc
        import lib.gpsbase as gpsbase
        import lib.gpsflymaster as gpsflymaster
    elif developer is False:
        from lib import gpsmisc
        from lib import gpsbase
        from lib import gpsflymaster
    else:
        print("Imported GPS devices from source, not signing IGCs")
        from . import gpsmisc
        from . import gpsbase
        from . import gpsflymaster

    modules = sys.modules.values()
    for module in modules:
        try:
            if module.implements_gps_device(module.__name__):
                GpsDevices.append(module)
        except (AttributeError, ImportError):
            pass
