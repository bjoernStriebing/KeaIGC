import os
import sys
import pkgutil

__all__ = ['GpsDevices']

if getattr(sys, 'frozen', False):
    import lib.gpsmisc as gpsmisc
    import lib.gpsbase as gpsbase
    import lib.gpsflymaster as gpsflymaster
elif '--developer' not in sys.argv:
    from lib import gpsmisc
    from lib import gpsbase
    from lib import gpsflymaster
else:
    print "Imported GPS devices from source, not signing IGCs"
    from . import gpsmisc
    from . import gpsbase
    from . import gpsflymaster

GpsDevices = []

pkgpath = os.path.dirname(__file__)
for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)]):
    try:
        module = eval(name)
        if module.implements_gps_device(module.__name__):
            GpsDevices.append(module)
    except Exception:
        pass
