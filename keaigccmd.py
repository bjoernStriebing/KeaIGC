import os
import Queue as queue
from glob import glob
from serial.serialutil import SerialException

import gpsdevice
from igc import save as igc_save
from library import utc_to_local


def run(args):
    # find the class in module
    gps_name = args.gps.lower()
    try:
        device = filter(lambda d: d.get_class(d).GUI_NAME.lower() == gps_name,
                        gpsdevice.GpsDevices)[0]
        # TODO: Warn on multiple matches
    except IndexError:
        # filter for gps name did not return anything
        print "ERROR: GPS class '{}' is not supported. Use --gps <class> to specify.\nValid options for <class> are (not case sensitive):".format(args.gps)
        for device in gpsdevice.GpsDevices:
            print '        {}'.format(device.get_class(device).GUI_NAME)
        exit(-1)

    # get instance and set the serial port
    try:
        gps = device.get_class(device)(port=args.serial)
    except (SerialException, AttributeError):
        print "ERROR: '{}' GPS device does not respond on port {}.\nOther candidates for argument --serial <path> are:".format(args.gps, args.serial)
        for serial in glob('/dev/tty.*'):
            if serial == args.serial:
                continue
            print '        {}'.format(serial)
        exit(-1)

    # get list of flights
    flight_queue = queue.Queue()
    gps.get_list(ret_queue=flight_queue)
    flights = {f.num: f for _, f in flight_queue.queue}

    if args.flights is None:
        print_flight_list(flights)
    else:

        if args.pilot is not None:
            gps.pilot_overwrite = ' '.join(args.pilot)

        if args.glider is not None:
            gps.glider_overwrite = ' '.join(args.glider)

        for flight_num in args.flights:
            try:
                timestamp = utc_to_local(flights[flight_num].datetime)
                filename = '{}.igc'.format(timestamp.strftime('%a %d-%b-%Y %H-%M'))
                output_file = os.path.join(args.out, filename)
                download_flight(gps, flight_num, output_file)
            except KeyError:
                print "Flight number {} is not available."
                print "Run command without -f and --flights option to see list of available flights."


def print_flight_list(flights):
    print "\n"
    print "No flight number specified."
    print "Use -f or --flights followed by list of flight numbers from list below.\n"
    print "       N         Date & Time         Duration"
    print "    ----    ---------------------   ---------"
    for num, flight in flights.iteritems():
        date_str = utc_to_local(flight.datetime).strftime("%a %_d %b %Y %_H:%M")
        duration = '{:2d}h {:2d}min'.format(
            *divmod(int(flight.duration.total_seconds() / 60), 60))
        duration = duration.replace('0h', '  ')
        entry = '{n:8d}    {date}   {dur}'.format(n=num, date=date_str, dur=duration)
        print entry
    print '\n'


def download_flight(gps, flight, output_file):
    output_file = os.path.expanduser(output_file)
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    try:
        igc_save.download(gps, flight, output_file)
    except igc_save.UnsignedIGCException as e:
        print 'IGC file "{}" not signed because gps module could not validated.'.format(
            output_file)
    home_path = os.path.expanduser('~')
    print' Flight {n} saved as "{f}"'.format(
        n=flight, f=output_file.replace(home_path, '~'))
