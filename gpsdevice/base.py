import serial
import operator
from collections import Iterable
from datetime import datetime, timedelta
from functools import reduce

from .misc import *

__all__ = ['GpsDeviceBase', 'GpsCommand',
           "crc_checksum", 'crc_checksum_hex']


class ResponseIdentification(Struct):
    """NMEA Identification resonse."""
    def __init__(self, model, pilot, serial, fw_version, _4, _5):
        self.model = model
        self.pilot = pilot
        self.serial = int(serial)
        self.fw_version = fw_version


class ResponseList(Struct):
    """NMEA GPS tracklist response."""
    def __init__(self, total, num, date, time, duration):
        t = datetime.strptime(duration, '%H:%M:%S')
        self.total = int(total)
        self.num = int(num)
        self.datetime = datetime.strptime(' '.join([date, time]), '%d.%m.%y %H:%M:%S')
        self.duration = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


class NMEAResponse(object):
    """Standard NMEA Response class converting raw data to specific response."""

    def __init__(self, gps, data):
        """Init with GPS device and raw data."""
        self.raw_data = data
        self.gps = gps

    def parse(self):
        """Parse raw_data and return respecive response object if crc valid."""
        stripped_data = self.raw_data.strip('$\r\n')
        self.data, crc = stripped_data.split('*')
        self.checksum = int(crc, 16)
        if not self.is_valid():
            return None
        return self.interprete()

    def is_valid(self):
        """Validate crc checksum against data."""
        return self.checksum == crc_checksum(self.data)

    def interprete(self):
        """Return actual response object depending on keyword in NMEA resonse."""
        data = self.data.split(',')
        kw = data[0]
        if kw == 'PFMSNP':
            response = ResponseIdentification(*data[1:])
            self.gps.progress = 1.0
        elif kw == 'PFMLST':
            response = ResponseList(*data[1:])
            self.gps.progress = float(response.num) / float(response.total)
        else:
            response = None
        return response


class GpsCommand(object):
    """
    Command object to be serialised and sent to the GPS device.

    Use "str(command)" to send composed message with checksum.
    """

    def __init__(self, command, response=True, data=None, mode='NMEA'):
        """Init """
        self.command = command
        self.response = response
        self.data = data
        self.mode = mode

    def __repr__(self):
        """Print class name and dict."""
        return '<%s %r>' % (self.__class__.__name__, self.__dict__)

    def __str__(self):
        """Compose the NMEA message with data fiels and calculate checksum."""
        cmd_str = self.command + ','
        if self.data is not None:
            cmd_str += ','.join(map(str, self.data))
            cmd_str += ','
        return '$' + cmd_str + '*' + crc_checksum_hex(cmd_str)


class GpsDeviceBase(object):
    """
    GPS device Base class.

    Offers basic send, and receive methods to communicate with the GPS device
    via serial port.
    """

    def __init__(self, port, **kwargs):
        """Initialise GPS device base class via serial port."""
        self.io = serial.Serial(port=port, baudrate=self.baudrate, timeout=.5)
        self.flush()
        self._manufacturer = None
        self._model = None
        self._serial = None
        self._fw_version = None
        self._gps_receiver = None

    @property
    def manufacturer(self):
        return str(self._manufacturer)

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def model(self):
        return str(self._model)

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def serial(self):
        return '{:05d}'.format(self._serial)

    @serial.setter
    def serial(self, value):
        self._serial = value

    @property
    def fw_version(self):
        return str(self._fw_version)

    @fw_version.setter
    def fw_version(self, value):
        self._fw_version = value

    @property
    def gps_receiver(self):
        return str(self._gps_receiver)

    @gps_receiver.setter
    def gps_receiver(self, value):
        self._gps_receiver = value

    def flush(self):
        """Empty serial buffer."""
        print self.io.readlines()

    def send(self, command, data=None):
        """
        Send command and optional data to GPS device.

        This will set the receive mode for the next reply to "NMEA" or "BIN"
        according to command attributes.
        """
        if data is not None:
            try:
                command.data += data
            except TypeError:
                command.data = data
        cmd_str = str(command)
        self.mode = command.mode
        self.io.write(cmd_str + '\r\n')
        self.progress = 0.0 if command.response else 1.0
        print '{:3.0f}%'.format(self.progress * 100), cmd_str

    def read(self, mode=None, progress_done_count=None):
        """
        Recieve response from GPS device.

        The response may be interpreted as NMEA type resonse or binary data.
        Respone mode should be set while sending the command that triggerd the
        response. It can also be forced with kwargs.
        """
        if mode is not None:
            self.mode = mode

        if self.mode == 'NMEA':
            return self._read_nmea()
        elif self.mode == 'BIN':
            return self._read_bin(progress_done_count=progress_done_count)

    def _read_nmea(self):
        """Read a NMEA response from GPS device."""
        data = self.io.readline()
        response = NMEAResponse(self, data)
        try:
            return response.parse()
        except ValueError:
            self.progress = 1.0
            return None

    def _read_bin(self, progress_done_count=None):
        """Read binary data transfer response from GPS device."""
        # TODO: NotImplemented
        pass

    def set_nav_off(self):
        """Stop sending current GPS fixes."""
        self.send(self._set_nav_off)

    def get_id(self):
        """Get NMEA Identification."""
        self.send(self._get_id)
        while self.progress < 1.0:
            response = self.read()
            self.model = response.model
            self.serial = response.serial
            self.fw_version = response.fw_version
            print '{:3.0f}%'.format(self.progress * 100), response

    def get_list(self):
        """Get NMEA GPS Tracklist."""
        self.tracklist = {}
        self.send(self._get_list)
        while self.progress < 1.0:
            response = self.read()
            try:
                self.tracklist[response.num] = response
            except Exception as e:
                pass
                # print e
            print '{:3.0f}%'.format(self.progress * 100), response

    def get_flight(self, num):
        """Download GPS tracklog."""
        try:
            entry = self.tracklist[int(num)]
        except KeyError:
            print 'Track number {} out of range'.format(num)
        flight_date = entry.datetime.strftime('%y%m%d%H%M%S')
        self.send(self._get_flight, data=[flight_date])
        # FIXME this assumes 1s fix interval
        return self.read(progress_done_count=entry.duration.total_seconds() + 1)


def crc_checksum(data):
    """
    Compute CRC checksum.

    XOR all data.
    Returns:
        int - checksum
    """
    try:
        cs = reduce(operator.xor, data, 0)
    except TypeError:
        cs = reduce(operator.xor, map(ord, data), 0)
    return cs


def crc_checksum_hex(data):
    """
    Compute CRC checksum.

    XOR all data.
    Returns:
        string - checksum in hex format
    """
    return '{:02X}'.format(crc_checksum(data))
