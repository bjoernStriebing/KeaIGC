import os
import Queue as queue
from threading import Thread
from glob import glob
from serial import SerialException
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp

from igc import save as igc_save
from gpsclassscreen import GpsClassScreen
from serialscreen import SerialScreen
from flightlistscreen import FlightListScreen
from popups.message import MessagePopup

import animation
from common import GuiColor


class KeaGpsDownloader(ScreenManager, GuiColor):

    busy = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(KeaGpsDownloader, self).__init__(**kwargs)
        self.device_screen = GpsClassScreen(name='devices')
        self.serial_screen = SerialScreen(name='ports')
        self.flightlist_screen = FlightListScreen(name='flightlist')
        self.add_widget(self.device_screen)
        self.add_widget(self.serial_screen)
        self.add_widget(self.flightlist_screen)
        self.current = 'devices'
        self.gps = None

    def device_selected(self, button, device):
        self.current = 'ports'
        if self.gps is None:
            self.gps = GpsInterface(self, device)
        # TODO else

    def port_selected(self, button, **kwargs):
        self.busy_indefinite()
        self.gps.set_port(button=button, **kwargs)

    def download_flight_header(self, flight):
        self.gps.download_flight_header(flight=flight)

    def is_busy(self):
        return self.busy is not None

    def busy_indefinite(self):
        if self.is_busy():
            return

        header = self.current_screen.ids.header
        width = header.width / (2 * 1.618)
        left = header.x
        right = header.x + header.width - width
        for rect in header.canvas.before.get_group('bar'):
            self.busy = animation.animate_size(width, rect.size[1])
            self.busy &= animation.animate_pos(right, rect.pos[1])
            self.busy.bind(on_complete=lambda *_: animation.move_left(header, rect, gui=self))
            self.busy.bind(on_complete=lambda *_: animation.stop(header, rect, gui=self))
            self.busy.start(rect)

    def busy_progress(self, progress):
        header = self.current_screen.ids.header
        width = header.width * progress
        left = header.x
        for rect in header.canvas.before.get_group('bar'):
            if self.busy is not None:
                self.busy.stop(rect)
            self.busy = animation.animate_pos(left, rect.pos[1], .05)
            self.busy &= animation.animate_size(width, rect.size[1], .05)
            self.busy.start(rect)
        if progress >= 1.0:
            self.busy = None

    def done(self):
        if not self.gps.joblist.empty():
            return
        animation = self.busy
        self.busy = None
        header = self.current_screen.ids.header
        for rect in header.canvas.before.get_group('bar'):
            try:
                animation.stop(rect)
            except AttributeError:
                pass

    @mainthread
    def show_map(self, flight_brief_header):
        self.current = 'flightlist'
        screen = self.get_screen('flightlist')
        screen.show_map()

    @mainthread
    def show_flights(self):
        self.current = 'flightlist'

    @mainthread
    def show_message(self, message):
        MessagePopup(message)


class KeaGpsApp(App):

    def build(self):
        self.gui = KeaGpsDownloader()
        return self.gui


class GpsInterface(Thread):

    def __init__(self, gui, device, **kwargs):
        self.joblist = queue.Queue()
        self.results = queue.Queue()
        self.gui = gui
        super(GpsInterface, self).__init__(target=self._target_func,
                                           args=(device, self.joblist), **kwargs)
        self.daemon = True
        self.start()

    def _threaded(func):
        def wrapper(self, **kwargs):
            self.joblist.put((func, kwargs))
        return wrapper

    @_threaded
    def set_port(self, button, port):
        try:
            self.gps.io = port
        except (SerialException, AttributeError, ValueError):
            button.disabled = True
            self.gui.show_message('Serial port "{}" does not match GPS device {}'.format(
                port, self.gps.__class__.GUI_NAME))
            return
        finally:
            self.gui.done()
        self.gui.show_flights()

    @_threaded
    def get_list(self):
        self.gui.busy_progress(0)
        Clock.schedule_once(lambda dt: self.gui.current_screen.add_flights(self.results), .02)
        self.gps.get_list(ret_queue=self.results)

    def download_flight_header(self, flight):
        Clock.schedule_once(lambda dt: self._poll_progress())
        header = self.gps.get_flight_brief(flight)
        self.gui.show_map(header)

    # @_threaded
    # def download_flight(self, flight):
    #     Clock.schedule_once(lambda dt: self._poll_progress(), .05)
    #     try:
    #         target_file = os.path.expanduser('~/Desktop/{}.igc'.format(self.gps.GUI_NAME))
    #         igc_save.download(self.gps, flight, target_file)
    #     except igc_save.UnsignedIGCException:
    #         self.gui.show_message("IGC file wasn't signed because there was a problem validating the GPS module")

    def _target_func(self, device, joblist):
        self.gps = device.get_class(device)(port=None)
        while True:
            func, kwargs = joblist.get()
            try:
                func(self, **kwargs)
            except Exception as e:
                print e

    def _poll_progress(self):
        progress = self.gps.progress
        self.gui.busy_progress(progress)
        if progress < 1.0:
            Clock.schedule_once(lambda dt: self._poll_progress(), .05)


if __name__ == '__main__':
    KeaPgApp().run()
