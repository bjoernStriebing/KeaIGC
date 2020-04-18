import os
import sys

__all__ = ['GpsDevices']

GpsDevices = set()


def import_lib(developer=False):
    global GpsDevices
    global gpsmisc
    global gpsbase
    global gpsflymaster

    frozen = getattr(sys, 'frozen', False)
    if frozen or developer is False:
        print("Imported GPS devices from libraries, will attempt signing IGCs")
        from .lib import gpsmisc
        from .lib import gpsbase
        from .lib import gpsflymaster
    else:
        print("Imported GPS devices from source, not signing IGCs")
        from . import gpsmisc
        from . import gpsbase
        from . import gpsflymaster

    modules = sys.modules.values()
    for module in modules:
        try:
            if module.implements_gps_device(module.__name__):
                GpsDevices.add(module)
        except (AttributeError, ImportError):
            pass
