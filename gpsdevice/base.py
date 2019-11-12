import serial
import operator
from binascii import hexlify
from datetime import datetime, timedelta
from functools import reduce

from .misc import *


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
        return self.checksum == _checksum(self.data)

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
            cmd_str += ','.join(map(str, data))
            cmd_str += ','
        return '$' + cmd_str + '*' + _checksum_hex(cmd_str)


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

    def flush(self):
        """Empty serial buffer."""
        print self.io.readlines()

    def send(self, command, data=None):
        """
        Send command and optional data to GPS device.

        This will set the receive mode for the next reply to "NMEA" or "BIN"
        according to command attributes.
        """
        data = command.compose(data)
        self.mode = command.mode
        self.io.write(data + '\r\n')
        self.progress = 0.0 if command.response else 1.0
        print '{:3.0f}%'.format(self.progress * 100), data

    def read(self, mode=None):
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
            return self._read_bin()

    def _read_nmea(self):
        """Read a NMEA response from GPS device."""
        data = self.io.readline()
        response = NMEAResponse(self, data)
        try:
            return response.parse()
        except ValueError:
            self.progress = 1.0
            return None

    def _read_bin(self):
        """Read binary data transfer response from GPS device."""
        packet_id = None
        while True:
            print '--------------------------------------------------------'
            packet = map(ord, self.io.read(2))
            packet_id = hexlify(bytearray(packet[0:2]))
            if packet_id == 'a3a3':
                'End of binary transmission\n'
                break

            packet += map(ord, self.io.read(1))
            packet_length = packet[2]

            packet += map(ord, self.io.read(packet_length))
            packet_data = packet[3:]

            packet += map(ord, self.io.read(1))
            packet_crc = packet[-1]

            if packet_id == 'a0a0':
                print 'Flight Information Record\n'
                print 'ID:      ', hexlify(bytearray(packet[0:2]))
                print 'length:  ', packet[2]
                print 'fw ver:  ', packet[3:5]
                print 'hw ver:  ', packet[5:7]
                print 'serial:  ', packet[7:11]
                print 'P number:', ''.join(map(chr, packet[11:19]))
                print 'P name:  ', ''.join(map(chr, packet[19:34]))
                print 'G brand: ', ''.join(map(chr, packet[34:49]))
                print 'G model: ', ''.join(map(chr, packet[49:64]))
                print 'unknown: ', packet[64:66]
                print 'CRC:     ', packet[66]
            elif packet_id == 'a1a1':
                print 'Key Track Position Record\n'
                print 'ID:      ', hexlify(bytearray(packet[0:2]))
                print 'length:  ', packet[2]
                print 'fix flag:', packet[3]
                print 'latitude:', int32(int(hexlify(bytearray(reversed(packet[4:8]))), 16)) / 60000.0
                print 'lngitude:', int32(int(hexlify(bytearray(reversed(packet[8:12]))), 16)) / -60000.0
                print 'altitude:', int16(int(hexlify(bytearray(reversed(packet[12:14]))), 16))
                print 'baro:    ', int16(int(hexlify(bytearray(reversed(packet[14:16]))), 16))
                print 'time:    ', datetime.utcfromtimestamp(int(hexlify(bytearray(reversed(packet[16:20]))), 16) + 946684800)
                print 'CRC:     ', packet[20]
                fix_count = 0
            elif packet_id == 'a2a2':
                offset = 0
                for _ in range(0, packet_length, 6):
                    print 'fix flag:', packet[offset + 3]
                    print 'latitude:', int8(int(packet[offset + 4])) / 60000.0
                    print 'lngitude:', int8(int(packet[offset + 5])) / 60000.0
                    print 'altitude:', int8(int(packet[offset + 6]))
                    print 'baro:    ', int8(int(packet[offset + 7]))
                    print 'time:    ', int(packet[offset + 8])
                    print ''
                    offset += 6
                    fix_count += 1
                print 'REMAINDER', packet[offset+3:-1]
                print 'Got {} fixes'.format(fix_count)

            if packet_crc == _checksum([packet_length] + packet_data):
                print '\nACK', packet_id, packet_length, 'crc', packet_crc
                self.io.write(b'\xb1')
            else:
                print '\nNACK', packet_id, packet_length, 'crc', packet_crc, '<->', _checksum([packet_length] + packet_data)
                self.io.write(b'\xb2')

            print '--------------------------------------------------------\n\n'

    def set_nav_off(self):
        """Stop sending current GPS fixes."""
        self.send(self._set_nav_off)

    def get_id(self):
        """Get NMEA Identification."""
        self.send(self._get_id)
        while self.progress < 1.0:
            response = self.read()
            print '{:3.0f}%'.format(self.progress * 100), response

    def get_list(self):
        """Get NMEA GPS Tracklist."""
        self.tracklist = {}
        self.send(self._get_list)
        while self.progress < 1.0:
            response = self.read()
            self.tracklist[response.num] = response
            print '{:3.0f}%'.format(self.progress * 100), response

    def get_flight(self, num):
        """Download GPS tracklog."""
        try:
            entry = self.tracklist[int(num)]
        except KeyError:
            print 'Track number {} out of range'.format(num)
        flight_date = entry.datetime.strftime('%y%m%d%H%M%S')
        self.send(self._get_flight, data=[flight_date])
        print self.read()


def _checksum(data):
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


def _checksum_hex(data):
    """
    Compute CRC checksum.

    XOR all data.
    Returns:
        string - checksum in hex format
    """
    return '{:02X}'.format(_checksum(data))
