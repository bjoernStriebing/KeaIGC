from binascii import hexlify
from datetime import datetime
from .base import *
from .misc import *


class ConstantsFlymaster(object):
    BAUDRATE = 57600
    EPOCH2000 = 946684800
    RADIANTS = 60000.0


class GpsFlymaster(GpsDeviceBase, ConstantsFlymaster):

    _set_nav_off = GpsCommand('PFMDNL', response=False)
    _set_nav_on = GpsCommand('PFMNAV', response=False)
    _set_pwoff = GpsCommand('PFMOFF')
    _get_id = GpsCommand('PFMSNP')
    _get_list = GpsCommand('PFMDNL', data=['LST'])
    _get_flight = GpsCommand('PFMDNL', mode='BIN')

    def __init__(self, port, **kwargs):
        self.baudrate = self.BAUDRATE
        # TODO: WIP disabled for faster testing
        # super(GpsFlymaster, self).__init__(port)

    def _read_bin(self):
        """Read binary data transfer response from GPS device."""
        last_fix = None
        tracklog = None
        fix_count = 0
        while True:
            # print '--------------------------------------------------------'
            packet = BinPacket()
            packet.id = self.io.read(2)
            if packet.id == 'a3a3':
                print 'End of binary transmission\n'
                return tracklog
            packet.length = self.io.read(1)
            packet.data = self.io.read(packet.length)
            packet.crc = self.io.read(1)

            if not packet.is_valid:
                print 'NACK', packet.id, packet.length, 'crc', packet.crc, '<->', crc_checksum([packet.length] + packet.data)
                self.io.write(b'\xb2')
                # print '--------------------------------------------------------\n\n'
                # TODO: max crc errors
                continue

            if packet.id == 'a0a0':
                # print 'Flight Information Record\n'
                fir = FlightInformationRecord(packet)
                # print 'ID:      ', packet.id
                # print 'length:  ', packet.length
                # print 'fw ver:  ', fir.firmware_version
                # print 'hw ver:  ', fir.hardware_version
                # print 'serial:  ', fir.serial
                # print 'P number:', fir.pilot_number
                # print 'P name:  ', fir.pilot_name
                # print 'G brand: ', fir.glider_brand
                # print 'G model: ', fir.glider_model
                # print 'CRC:     ', packet.crc
            elif packet.id == 'a1a1':
                # print 'Key Track Position Record\n'
                last_fix = key_record = KeyTrackPositionRecord(packet)
                tracklog = [key_record]
                fix_count = 1
                # print 'ID:      ', packet.id
                # print 'length:  ', packet.length
                # print 'fix flag:', key_record.fix_flag
                # print 'latitude:', key_record.latitude
                # print 'lngitude:', key_record.longitude
                # print 'altitude:', key_record.altitude_gps
                # print 'baro:    ', key_record.altitude_baro
                # print 'time:    ', key_record.timestamp
                # print 'CRC:     ', packet.crc
            elif packet.id == 'a2a2':
                offset = 0
                for _ in range(0, packet.length, 6):
                    fix = DiffPositionRecord(packet, offset=offset, ref_record=last_fix)
                    tracklog.append(fix)
                    # print 'fix flag:', fix.fix_flag
                    # print 'latitude:', fix.latitude
                    # print 'lngitude:', fix.longitude
                    # print 'altitude:', fix.altitude_gps
                    # print 'baro:    ', fix.altitude_baro
                    # print 'time:    ', fix.timestamp
                    # print ''
                    offset += 6
                    fix_count += 1
                    last_fix = fix
                # print 'Got {} fixes'.format(fix_count)

            print 'ACK', packet.id, packet.length, 'crc', packet.crc
            self.io.write(b'\xb1')
            return fir, key_record, tracklog
            # print '--------------------------------------------------------\n\n'


class BinPacket(Struct):

    def __init__(self, **kwargs):
        self._payload_offset = 0
        self._valid = False
        self.__data = []

    def __getitem__(self, value):
        return self.__data[value]

    @property
    def is_valid(self):
        return self._valid

    @property
    def id(self):
        id_len = self._payload_offset - 1
        return ''.join(map(str, self.__data[0:id_len]))

    @id.setter
    def id(self, value):
        id = hexlify(bytearray(value))
        self.__data[0:len(id)] = [id[i:i + 2] for i in range(0, len(id), 2)]
        self._payload_offset = len(value) + 1  # +1 for length

    @property
    def length(self):
        return int(self.__data[self._payload_offset - 1])

    @length.setter
    def length(self, value):
        v = ord(value)
        i = self._payload_offset - 1
        self.__data[i:i + 1] = [v]

    @property
    def data(self):
        return self.__data[self._payload_offset:-1]

    @data.setter
    def data(self, value, crc=None):
        payload = map(ord, value)
        self.__data = self.__data[:self._payload_offset] + payload + [crc]
        if crc is None:
            self._valid = False
        else:
            self._valid = (crc == crc_checksum([self.length] + self.data))

    @property
    def crc(self):
        return self.__data[-1]

    @crc.setter
    def crc(self, value):
        crc = ord(value)
        i = self._payload_offset + self.length
        self.__data[i] = crc
        self._valid = (crc == crc_checksum([self.length] + self.data))


class FlightInformationRecord(Struct):

    def __init__(self, packet, **kwargs):
        self.firmware_version = packet[3:5]
        self.hardware_version = packet[5:7]
        self.serial = packet[7:11]
        self.pilot_number = packet[11:19]
        self.pilot_name = packet[19:34]
        self.glider_brand = packet[34:49]
        self.glider_model = packet[49:64]

    @property
    def pilot_number(self):
        return self._pilot_number

    @pilot_number.setter
    def pilot_number(self, value):
        self._pilot_number = ''.join(map(chr, value))

    @property
    def pilot_name(self):
        return self._pilot_name

    @pilot_name.setter
    def pilot_name(self, value):
        self._pilot_name = ''.join(map(chr, value))

    @property
    def glider_brand(self):
        return self._glider_brand

    @glider_brand.setter
    def glider_brand(self, value):
        self._glider_brand = ''.join(map(chr, value))

    @property
    def glider_model(self):
        return self._glider_model

    @glider_model.setter
    def glider_model(self, value):
        self._glider_model = ''.join(map(chr, value))


class PositionRecord(Struct, ConstantsFlymaster):

    def __add__(self, record):
        self._latitude += record._latitude
        self._longitude += record._longitude
        self._altitude_gps += record._altitude_gps
        self._altitude_baro += record._altitude_baro
        self._timestamp += record._timestamp

    @property
    def fix_flag(self):
        return self._fix_flag

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def altitude_gps(self):
        return self._altitude_gps

    @property
    def altitude_baro(self):
        return self._altitude_baro

    @property
    def timestamp(self):
        return datetime.utcfromtimestamp(self._timestamp + self.EPOCH2000)

    @fix_flag.setter
    def fix_flag(self, value):
        self._fix_flag = value

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = self._bin2int(value)

    def _bin2int(self, bytes):
        if isinstance(bytes, list):
            return int(hexlify(bytearray(reversed(bytes))), 16)
        else:
            return int(bytes)


class KeyTrackPositionRecord(PositionRecord):

    def __init__(self, packet, **kwargs):
        self.fix_flag = packet[3]
        self.latitude = packet[4:8]
        self.longitude = packet[8:12]
        self.altitude_gps = packet[12:14]
        self.altitude_baro = packet[14:16]
        self.timestamp = packet[16:20]

    @property
    def latitude(self):
        return self._latitude / self.RADIANTS

    @latitude.setter
    def latitude(self, value):
        self._latitude = int32(self._bin2int(value))

    @property
    def longitude(self):
        return self._longitude / -self.RADIANTS

    @longitude.setter
    def longitude(self, value):
        self._longitude = int32(self._bin2int(value))

    @property
    def altitude_gps(self):
        return self._altitude_gps

    @altitude_gps.setter
    def altitude_gps(self, value):
        self._altitude_gps = int16(self._bin2int(value))

    @property
    def altitude_baro(self):
        return self._altitude_baro

    @altitude_baro.setter
    def altitude_baro(self, value):
        self._altitude_baro = int16(self._bin2int(value))


class DiffPositionRecord(PositionRecord):

    def __init__(self, packet, offset=0, ref_record=None, **kwargs):
        self.fix_flag = packet[offset + 3]
        self.latitude = packet[offset + 4]
        self.longitude = packet[offset + 5]
        self.altitude_gps = packet[offset + 6]
        self.altitude_baro = packet[offset + 7]
        self.timestamp = packet[offset + 8]

        if ref_record is not None:
            self.__add__(ref_record)


    @property
    def latitude(self):
        return self._latitude / self.RADIANTS

    @latitude.setter
    def latitude(self, value):
        self._latitude = int8(self._bin2int(value))

    @property
    def longitude(self):
        return self._longitude / -self.RADIANTS

    @longitude.setter
    def longitude(self, value):
        self._longitude = int8(self._bin2int(value))

    @property
    def altitude_gps(self):
        return self._altitude_gps

    @altitude_gps.setter
    def altitude_gps(self, value):
        self._altitude_gps = int8(self._bin2int(value))

    @property
    def altitude_baro(self):
        return self._altitude_baro

    @altitude_baro.setter
    def altitude_baro(self, value):
        self._altitude_baro = int8(self._bin2int(value))
