# coding=utf-8
"""
MapView
=======

.. author:: Mathieu Virbel <mat@kivy.org>

MapView is a Kivy widget that display maps.
"""

__all__ = ["Coordinate", "Bbox", "MapView", "MapSource", "MapMarker",
           "MapLayer", "MarkerMapLayer", "MapMarkerPopup"]
__version__ = "0.2"

MIN_LATITUDE = -90.
MAX_LATITUDE = 90.
MIN_LONGITUDE = -180.
MAX_LONGITUDE = 180.
CACHE_DIR = '/tmp/keagps/cache'

try:
    # fix if used within garden
    import sys
    sys.modules['mapview'] = sys.modules['kivy.garden.mapview.mapview']
    del sys
except KeyError:
    pass

from types import Coordinate, Bbox
from source import MapSource
from view import MapView, MapMarker, MapLayer, MarkerMapLayer, \
    MapMarkerPopup