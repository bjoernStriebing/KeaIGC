import sys

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
