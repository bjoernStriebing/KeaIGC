from datetime import datetime
from functools import reduce
from operator import __add__
from gpsdevice.gpsbase import *
from gpsdevice.gpsmisc import *


class ConstantsFlymaster(object):
    EPOCH2000 = 946684800
    RADIANTS = 60000.0


class GpsFlymaster(GpsDeviceBase, ConstantsFlymaster):

    GUI_NAME = "Flymaster"
    MANUFACTURER_NAMES = ["Flymaster"]
    MODEL_NAMES = ["ANY"]
    BAUDRATE = 57600
    _set_nav_off = GpsCommand('PFMDNL', response=False)
    _set_nav_on = GpsCommand('PFMNAV', response=False)
    _set_pwoff = GpsCommand('PFMOFF', response=False)
    _get_id = GpsCommand('PFMSNP')
    _get_list = GpsCommand('PFMDNL', data=['LST'])
    _get_flight = GpsCommand('PFMDNL', mode='BIN')

    def __init__(self, port, **kwargs):
        self.baudrate = self.BAUDRATE
        super(GpsFlymaster, self).__init__(port)

    @property
    def io(self):
        return super(GpsFlymaster, self).io

    @io.setter
    def io(self, port):
        super(GpsFlymaster, self.__class__).io.fset(self, port)
        if self._io is not None:
            self.set_nav_off()
            self.get_id()
            self.validate_id()

    def get_id(self):
        super(GpsFlymaster, self).get_id()
        self.manufacturer = self._manufacturer or 'Flymaster'

    def _read_bin(self, progress_done_count=None, header_only=False):
        """Read binary data transfer response from GPS device."""
        last_fix = None
        tracklog = None
        key_record = None
        fix_count = 0
        while True:
            # print('--------------------------------------------------------')
            packet = BinPacket()
            packet.id = self.io.read(2)
            if packet.id == 'a3a3':
                self.io.write(b'\xb1')
                try:
                    return fir, key_record, tracklog
                except UnboundLocalError:
                    return self._fir, self._kr, tracklog
            elif packet.id == '0000':
                # undocumented mystery packet sent between consecutive downloads
                # first listen to all it has to say
                # then politly knod and smile so we get to the actual data
                while self.io.read(1):
                    pass
                self.io.write(b'\xb1')
                continue
            packet.length = self.io.read(1)
            packet.data = self.io.read(packet.length)
            packet.crc = self.io.read(1)

            if not packet.is_valid:
                # print('NACK', packet.id, packet.length, 'crc', packet.crc, '<->', crc_checksum([packet.length] + packet.data))
                self.io.write(b'\xb2')
                # print('--------------------------------------------------------\n\n')
                # TODO: max crc errors
                continue

            if packet.id == 'a0a0':
                # print('Flight Information Record\n')
                fir = self._fir = FlightInformationRecord(packet)
                # print('ID:      ', packet.id)
                # print('length:  ', packet.length)
                # print('fw ver:  ', fir.firmware_version)
                # print('hw ver:  ', fir.hardware_version)
                # print('serial:  ', fir.serial)
                # print('P number:', fir.pilot_number)
                # print('P name:  ', fir.pilot_name)
                # print('G brand: ', fir.glider_brand)
                # print('G model: ', fir.glider_model)
                # print('CRC:     ', packet.crc)
            elif packet.id == 'a1a1':
                # print('Key Track Position Record\n')
                last_fix = self._kr = key_record = KeyTrackPositionRecord(packet)
                tracklog = self._tl = [key_record]
                fix_count = 1
                # print('ID:      ', packet.id)
                # print('length:  ', packet.length)
                # print('fix flag:', key_record.fix_flag)
                # print('latitude:', key_record.latitude)
                # print('lngitude:', key_record.longitude)
                # print('altitude:', key_record.altitude_gps)
                # print('baro:    ', key_record.altitude_baro)
                # print('time:    ', key_record.timestamp)
                # print('CRC:     ', packet.crc)
                if header_only:
                    self.io.write(b'\xb3')
                    self.progress = 1
                    try:
                        return fir, key_record, tracklog
                    except UnboundLocalError:
                        return self._fir, key_record, tracklog
            elif packet.id == 'a2a2':
                offset = 0
                for _ in range(0, packet.length, 6):
                    fix = DiffPositionRecord(packet, offset=offset, ref_record=last_fix)
                    try:
                        tracklog.append(fix)
                    except AttributeError:
                        tracklog.append(fix)
                    # print('fix flag:', fix.fix_flag)
                    # print('latitude:', fix.latitude)
                    # print('lngitude:', fix.longitude)
                    # print('altitude:', fix.altitude_gps)
                    # print('baro:    ', fix.altitude_baro)
                    # print('time:    ', fix.timestamp)
                    # print('')
                    offset += 6
                    fix_count += 1
                    last_fix = fix
                # print('Got {} fixes'.format(fix_count))

            if progress_done_count is not None:
                self.progress = float(fix_count) / progress_done_count
                # print('{:3.0f}%'.format(self.progress * 100), last_fix or fir)
            self.io.write(b'\xb1')
        # print('--------------------------------------------------------\n\n')
        # TODO break on error and returns

    def get_flight_brief(self, num):
        """Download Flight Information Record and Key Position only."""
        fir, kpr, _ = super(GpsFlymaster, self).get_flight_brief(num)
        return TrackHeader(latitude=kpr.latitude, longitude=kpr.longitude,
                           alt_gps=kpr.altitude_gps, alt_baro=kpr.altitude_baro,
                           timestamp=kpr.timestamp, pilot_name=fir.pilot_name,
                           glider_name=' '.join([fir.glider_brand, fir.glider_model]))


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
        id = value.hex()
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
        payload = list(value)
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
        try:
            crc = ord(value)
        except TypeError:
            crc = 0
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
        try:
            s = ''.join(map(chr, value))
            if isinstance(s, bytes):
                self._pilot_number = s.decode()
            else:
                self._pilot_number = s
        except TypeError:
            self._pilot_number = value

    @property
    def pilot_name(self):
        return self._pilot_name

    @pilot_name.setter
    def pilot_name(self, value):
        try:
            s = ''.join(map(chr, value))
            if isinstance(s, bytes):
                self._pilot_name = s.decode()
            else:
                self._pilot_name = s
        except TypeError:
            self._pilot_name = value

    @property
    def glider_brand(self):
        return self._glider_brand

    @glider_brand.setter
    def glider_brand(self, value):
        try:
            s = ''.join(map(chr, value))
            if isinstance(s, bytes):
                self._glider_brand = s.decode()
            else:
                self._glider_brand = s
        except TypeError:
            self._glider_brand = value

    @property
    def glider_model(self):
        return self._glider_model

    @glider_model.setter
    def glider_model(self, value):
        try:
            s = ''.join(map(chr, value))
            if isinstance(s, bytes):
                self._glider_model = s.decode()
            else:
                self._glider_model = s
        except TypeError:
            self._glider_model = value

    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, value):
        self._serial = sum([value[i] << 8 * i for i in range(len(value))])

    @property
    def firmware_version(self):
        return self._firmware_version

    @firmware_version.setter
    def firmware_version(self, value):
        self._firmware_version = '.'.join(map(str, value))

    @property
    def hardware_version(self):
        return self._hardware_version

    @hardware_version.setter
    def hardware_version(self, value):
        self._hardware_version = '.'.join(map(str, value))


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
            return reduce(lambda msb, lsb: (msb << 8) + lsb, reversed(bytes))
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
