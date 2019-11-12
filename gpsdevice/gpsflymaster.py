from .base import *


class GpsFlymaster(GpsDeviceBase):

    _set_nav_off = GpsCommand('PFMDNL', response=False)
    _set_nav_on = GpsCommand('PFMNAV', response=False)
    _set_pwoff = GpsCommand('PFMOFF')
    _get_id = GpsCommand('PFMSNP')
    _get_list = GpsCommand('PFMDNL', data=['LST'])
    _get_flight = GpsCommand('PFMDNL', mode='BIN')

    def __init__(self, port, **kwargs):
        self.baudrate = 57600
        super(GpsFlymaster, self).__init__(port)
