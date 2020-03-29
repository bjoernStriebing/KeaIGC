import os
import sys
import pytz
import errno
from tzlocal import get_localzone
aerofiles_path = os.path.join(os.path.dirname(__file__), 'aerofiles')
sys.path.append(aerofiles_path)

import aerofiles                                                        # nopep8

__all__ = ['aerofiles',
           'mkdir_p', 'utc_to_local']

local_tz = get_localzone()


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)


# TODO: not required in python3
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
