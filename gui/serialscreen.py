import os
from glob import glob
from functools import partial
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.metrics import *

from .common import GuiLabel, GuiButton
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
                on_release: Clock.schedule_once(lambda dt: root.list_serial_ports(False))
""")


class SerialScreen(Screen):

    def on_enter(self, **kwargs):
        super(SerialScreen, self).on_pre_enter(**kwargs)
        self.list_serial_ports()

    def list_serial_ports(self, reschedule=True):
        ports = list(map(lambda p: {'path': p, 'short': p.split('.')[1]},
                         glob('/dev/tty.*')))
        # add missing ports
        for port in ports:
            if not port['short'].startswith('usbmodem'):
                continue
            if port['short'] in [b.text for b in self.ids.list_bl.children]:
                continue
            b = GuiButton(text=port['short'])
            b.bind(on_release=partial(self.manager.port_selected, port=port['path']))
            self.ids.list_bl.add_widget(b)
        # throw out old ones
        for button in self.ids.list_bl.children:
            if button.text not in map(lambda p: p['short'], ports):
                self.ids.list_bl.remove_widget(button)
        # do it all again soon
        if reschedule and self.manager.current_screen == self:
            Clock.schedule_once(lambda dt: self.list_serial_ports(), 1)

    def go_back(self, *largs):
        self.manager.current = 'devices'
