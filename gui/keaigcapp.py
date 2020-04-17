import os
import queue
from threading import Thread
from glob import glob
from serial import SerialException
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.relativelayout import RelativeLayout
from kivy.metrics import dp

from igc import save as igc_save
from .gpsclassscreen import GpsClassScreen
from .serialscreen import SerialScreen
from .flightlistscreen import FlightListScreen
from .settingsscreen import SettingsScreen
from .popups.message import MessagePopup
from .popups.confirm import ConfirmPopup

from . import animation
from .common import GuiColor, GuiImgButton

Config.set('kivy', 'exit_on_escape', '0')
Config.setdefaults('user', {'auto_detect_ports': None})

Builder.load_string("""
<RootWidget>:
    main_screen: main_screen
    blur_effect: blur_effect.__self__

    KeaIgcDownloader:
        id: main_screen
        pos: 0, 0
        size_hint: 1, 1

    GuiImgButton:
        pos: root.width - self.width - dp(12), root.height - self.height - dp(12)
        size: dp(26), dp(26)
        size_hint: None, None
        opacity: .12
        on_release: root.show_settings()
        source: 'gui/img/settings.png'

    Image:
        id: blur_effect
        pos: 0, 0
        size_hint: 1, 1
        # TODO rerender the image on window resize instead of stetching the
        allow_stretch: True
        keep_ratio: False
""")


class RootWidget(RelativeLayout):
    blur_effect = ObjectProperty()
    main_screen = ObjectProperty()

    def __init__(self, **kwargs):
        Window.clearcolor = (1, 1, 1, 1)
        super(RootWidget, self).__init__(**kwargs)

    def on_parent(self, instance, parent):
        if parent is not None:
            self.remove_widget(self.blur_effect)  # remove effect for performace

    def show_settings(self):
        self.ids.main_screen.current = 'settings'


class KeaIgcDownloader(ScreenManager, GuiColor):

    busy = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(KeaIgcDownloader, self).__init__(**kwargs)
        self.last_screen = None
        self.device_screen = GpsClassScreen(name='devices')
        self.serial_screen = SerialScreen(name='ports')
        self.flightlist_screen = FlightListScreen(name='flightlist')
        self.settings_screen = SettingsScreen(name='settings')
        self.add_widget(self.device_screen)
        self.add_widget(self.serial_screen)
        self.add_widget(self.flightlist_screen)
        self.add_widget(self.settings_screen)
        self.current = 'devices'
        self.gps = None

    @mainthread
    def device_selected(self, *args):
        self.current = 'ports'
        try:
            _, device = args
            if self.gps is not None:
                del(self.gps)
            self.gps = GpsInterface(self, device)
        except ValueError:
            pass

    def on_current(self, instance, value):
        if self.last_screen != self.current_screen:
            self.last_screen = self.current_screen
        super(KeaIgcDownloader, self).on_current(instance, value)

    def download_flight_header(self, flight):
        self.gps.download_flight_header(flight=flight)

    def download_flight(self, flight, output_file):
        self.gps.download_flight(flight=flight, output_file=output_file)

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

    @mainthread
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

    @mainthread
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
    def show_map(self, flight_num, flight_brief_header):
        self.current = 'flightlist'
        screen = self.get_screen('flightlist')
        screen.show_map(flight_num, flight_brief_header)

    @mainthread
    def unselect_flight(self, flight):
        screen = self.get_screen('flightlist')
        screen.unselect_flight(flight)

    @mainthread
    def show_flights(self):
        self.current = 'flightlist'

    @mainthread
    def show_message(self, message):
        MessagePopup(message)

    @mainthread
    def suggest_update(self, release_ver, my_ver, dl_size, continue_update):
        ConfirmPopup("An update is available.\n\nYour version is {}.\n\n\nDownload {:.1f} MB to upgrade to version {}?".format(
                     my_ver, dl_size / 1000000, release_ver),
                     ok_callback=lambda e=continue_update: e.set())


class KeaIgcApp(App):

    def build(self):
        self.icon = 'gui/img/app_icon.png'
        self.root_widget = RootWidget()
        self.gui = self.root_widget.main_screen
        Window.bind(on_request_close=self.on_request_close)
        return self.root_widget

    def on_request_close(self, *args):
        try:
            Config.write()
        except Exception:
            pass


class GpsInterface(Thread):

    def __init__(self, gui, device, **kwargs):
        self.joblist = queue.Queue()
        self.results = queue.Queue()
        self.gui = gui
        super(GpsInterface, self).__init__(target=self._target_func,
                                           args=(device, ), **kwargs)
        self.daemon = True
        self.polling = None
        self.start()

    def _threaded(func):
        def wrapper(self, **kwargs):
            self.joblist.put((func, kwargs))
        return wrapper

    @_threaded
    def set_port(self, port, button):
        try:
            self.gps.io = port['path']
        except (SerialException, AttributeError, ValueError) as e:
            if button is None:
                # port not valid on automatic scanning
                self.results.put((False, port))
            else:
                button.disabled = True
                self.gui.show_message('Serial port "{}" does not match GPS device {}'.format(
                    port['path'], self.gps.__class__.GUI_NAME))
            return
        else:
            if button is None:
                # success on automatic port scanning
                self.results.put((True, port))
                self.drop_jobs()
        finally:
            self.gui.done()
        self.gui.show_flights()

    def drop_jobs(self):
        while True:
            try:
                self.joblist.get_nowait()
            except queue.Empty:
                break

    @_threaded
    def get_list(self):
        self.gui.busy_progress(0)
        Clock.schedule_once(lambda dt: self.gui.current_screen.add_flights(self.results), .02)
        self.gps.get_list(ret_queue=self.results)

    @_threaded
    def download_flight_header(self, flight):
        if self.polling is None:
            self.poppling = Clock.schedule_once(lambda dt: self._poll_progress())
        header = self.gps.get_flight_brief(flight)
        self.gui.show_map(flight, header)

    @_threaded
    def download_flight(self, flight, output_file):
        if self.polling is None:
            Clock.schedule_once(lambda dt: self._poll_progress(), .05)
        try:
            output_file = os.path.expanduser(output_file)
            output_dir = os.path.dirname(output_file)
            os.makedirs(output_dir, exist_ok=True)
            igc_save.download(self.gps, flight, output_file)
        except igc_save.UnsignedIGCException:
            self.gui.show_message("IGC file wasn't signed because there was a problem validating the GPS module")
        else:
            home_path = os.path.expanduser('~')
            self.gui.show_message("Signed IGC saved at {}".format(output_file.replace(home_path, '~')))
        self.gui.unselect_flight(flight)

    def set_pilot_overwrite(self, overwrite):
        self.gps.pilot_overwrite = overwrite

    def set_glider_overwrite(self, overwrite):
        self.gps.glider_overwrite = overwrite

    def _target_func(self, device):
        self.gps = device.get_class(device)(port=None)
        while True:
            func, kwargs = self.joblist.get()
            try:
                func(self, **kwargs)
            except SerialException:
                # presumably device has been disconnected
                self.gui.show_message("Connection Error. Please make sure your USB cable is connected securely.")
                self.gui.device_selected()
            except Exception as e:
                print(e)

    def _poll_progress(self):
        progress = self.gps.progress
        self.gui.busy_progress(progress)
        if progress < 1.0:
            self.polling = Clock.schedule_once(lambda dt: self._poll_progress(), .05)
        else:
            self.polling = None
