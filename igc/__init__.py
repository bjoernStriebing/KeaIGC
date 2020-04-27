import sys
from . import vali

__all__ = ['save']

save = None


class open_igc_save():

    def download(self, instrument, flightnumber, igc_filename):
        # get tracklog
        fir, key_record, tracklog = instrument.get_flight(flightnumber)
        # write to file
        with open(igc_filename, 'wb') as igc_file:
            igc_writer = aerofiles.IGCWriter(igc_file)
            igc_writer.write_headers(
                {'manufacturer_code': 'XEA',
                 'logger_id': instrument.model,
                 'date': key_record.timestamp.date(),
                 'pilot': fir.pilot_name.strip(),
                 'glider_type': ' '.join([fir.glider_brand, fir.glider_model]).strip(),
                 'logger_type': ' '.join([instrument.manufacturer, instrument.model]),
                 'logger_id_extension': fir.serial,
                 'gps_receiver': instrument.gps_receiver,
                 'firmware_version': fir.firmware_version,
                 'hardware_version': fir.hardware_version})

            # add fixes to igc
            for fix in tracklog:
                igc_writer.write_fix(
                    fix.timestamp.time(),
                    latitude=fix.latitude,
                    longitude=fix.longitude,
                    valid='A' if fix.fix_flag & 0x01 else 'V',
                    pressure_alt=fix.altitude_baro,
                    gps_alt=fix.altitude_gps)

            # write (header + tracklog)
            data = igc_writer.dump_text()


def import_lib(open_lib=False):
    global save
    if open_lib:
        from library import aerofiles
        save = open_igc_save()
    else:
        try:
            if getattr(sys, 'frozen', False):
                raise ImportError("Need to import from library in frozen application")

            from ._private import save as igc_save
            print("Imported private IGC signing source successfully")

        except ImportError as e:
            # print(e)  # debug
            print("Import IGC signing from shared object")
            from . import save as igc_save
        save = igc_save
