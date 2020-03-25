import pytz
import Queue as queue
from tzlocal import get_localzone
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.metrics import *

from common import GuiLabel, GuiButton
import gpsdevice

local_tz = get_localzone()

Builder.load_string("""
<FlightListScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        GuiLabel:
            size_hint: 1, None
            height: dp(40)
            text: "Select flights from list below"
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
                text: "Download"
""")


class FlightListScreen(Screen):

    def on_pre_enter(self, **kwargs):
        super(FlightListScreen, self).on_pre_enter(**kwargs)
        self.list_flights()

    def list_flights(self):
        self.ids.list_bl.clear_widgets()
        self.manager.gps.get_list()

    @mainthread
    def add_flights(self, flight_queue):
        try:
            progress, flight = flight_queue.get_nowait()
        except queue.Empty:
            Clock.schedule_once(lambda dt: self.add_flights(flight_queue), .02)
            return
        if progress < 1.0:
            Clock.schedule_once(lambda dt: self.add_flights(flight_queue), .02)
        # add a button for the flight
        date_str = utc_to_local(flight.datetime).strftime("%A\n%d %b %Y\n%H:%M")
        self.ids.list_bl.add_widget(
            GuiButton(text=date_str,
                      on_release=lambda x, n=flight.num: Clock.schedule_once(lambda dt: self.manager.download_flight(n))))

    def go_back(self, *largs):
        self.manager.current = 'ports'


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
