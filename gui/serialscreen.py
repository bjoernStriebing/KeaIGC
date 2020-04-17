import os
from glob import glob
from threading import Thread
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.metrics import *

from .common import GuiLabel, GuiButton
from .popups.confirm import ConfirmPopup
from .popups.message import MessagePopup
import gpsdevice


Builder.load_string("""
<SerialScreen>:
    BoxLayout:
        id: list_bl
        orientation: "vertical"
""")

Builder.load_string("""
#:import Clock kivy.clock.Clock
<SerialScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        ScreenHeader:
            id: header
            text: "Please select the Port your GPS device is connected to"
        ScrollView:
            bar_width: 3
            scroll_distance: dp(20)
            scroll_wheel_distance: dp(20)
            smooth_scroll_end: 8
            GuiGridLayout:
                id: list_bl
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            id: buttom
            size_hint: 1, None
            height: self.minimum_height
            spacing: dp(7)
            GuiButton:
                text: "Back"
                on_release: Clock.schedule_once(lambda dt: root.go_back())
            GuiButton:
                text: "Reload Ports"
                on_release: Clock.schedule_once(lambda dt: root.update_port_buttons(False))
""")


class SerialScreen(Screen):

    def on_enter(self, **kwargs):
        super(SerialScreen, self).on_pre_enter(**kwargs)
        try:
            auto_detect_ports = Config.getboolean('user', 'auto_detect_ports')
        except ValueError:
            auto_detect_ports = None
            self.ask_auto_detect_ports()

        if auto_detect_ports:
            self.detect_port(enable_popup=True)
        else:
            self.update_port_buttons()

    def update_port_buttons(self, reschedule=True):
        ports = list(self.find_serial_ports())
        # add missing ports
        for port in ports:
            b = None
            for b in filter(lambda b: port['short'] == b.text, self.ids.list_bl.children):
                if not reschedule:
                    b.disabled = False
            if b is not None:
                continue
            b = GuiButton(text=port['short'])
            b.bind(on_release=lambda b=b, p=port: self.port_button_cb(b, p))
            self.ids.list_bl.add_widget(b)
        # throw out old ones
        self.clear_dropped_ports(ports)
        # do it all again soon
        if reschedule and self.manager.current_screen == self:
            Clock.schedule_once(lambda dt: self.update_port_buttons(), 1)

    def port_button_cb(self, button, port):
        self.manager.busy_indefinite()
        self.manager.gps.set_port(port=port, button=button)

    def detect_port(self, enable_popup=False):
        self.manager.busy_indefinite()
        ports = list(self.find_serial_ports())
        for port in ports:
            self.manager.gps.set_port(port=port, button=None)
        self.clear_dropped_ports(ports)
        if len(ports) == 0:
            if enable_popup:
                MessagePopup("No devices found.\n\nPlease make sure you'r GPS device is turned on and connected.")
            self.manager.done()
            if self.manager.current_screen == self:
                Clock.schedule_once(lambda dt: self.detect_port(), 1)
            return
        else:
            t = Thread(target=self._check_auto_port_results,
                       args=(len(ports), ))
            t.daemon = True
            t.start()

    def clear_dropped_ports(self, ports):
        try:
            for button in self.ids.list_bl.children:
                if button.text not in map(lambda p: p['short'], ports):
                    self.ids.list_bl.remove_widget(button)
        except TypeError:
            self.ids.list_bl.clear_widgets()

    def find_serial_ports(self):
        ports = map(lambda p: {'path': p, 'short': p.split('.')[1]},
                    glob('/dev/tty.*'))
        return filter(lambda p: p['short'].startswith('usbmodem'), ports)

    def ask_auto_detect_ports(self):
        Config.add_callback(lambda s, k, detect: self.detect_port(enable_popup=True) if detect else None,
                            section='user', key='auto_detect_ports')
        ConfirmPopup('Do you want to enable automatic checking for suitable devices?\nAnswering YES will attempt to talk to all USB serial devices you may have connected.\n\nYou can always disable this in the settings.',
                     ok_callback=lambda: Config.set('user', 'auto_detect_ports', True),
                     cancel_callback=lambda: Config.set('user', 'auto_detect_ports', False))

    def go_back(self, *largs):
        self.manager.current = 'devices'

    def _check_auto_port_results(self, num_ports, *args):
        gps_interface = self.manager.gps
        for _ in range(num_ports):
            valid, port = gps_interface.results.get()
            if valid:
                return
            else:
                b = GuiButton(text=port['short'], disabled=True)
                b.bind(on_release=lambda b=b, p=port: self.port_button_cb(b, p))
                self.ids.list_bl.add_widget(b)
        self._message_no_valid_port()

    @mainthread
    def _message_no_valid_port(self):
        MessagePopup("None of the available ports matches your device{}.\n\nPlease make sure you'r GPS device is turned on and connected.".format(self.manager.gps.GUI_NAME))
