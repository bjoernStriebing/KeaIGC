import pytz
import Queue as queue
from tzlocal import get_localzone
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, ObjectProperty
from kivy.metrics import *

from common import GuiLabel, GuiButton, GuiSelsectButton
import gpsdevice
import animation
from contrib.gardenmapview import MapView, MapMarkerPopup

local_tz = get_localzone()

Builder.load_string("""
<FlightListScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        ScreenHeader:
            id: header
            text: "Select flights from list below"
        FloatLayout:
            ScrollView:
                id: listbox
                size_hint: 1, 1
                pos_hint: {'x': 0, 'y': 0}
                bar_width: 3
                scroll_distance: dp(20)
                scroll_wheel_distance: dp(20)
                smooth_scroll_end: 8
                GuiGridLayout:
                    id: list_bl
                    size_hint_y: None
                    height: self.minimum_height
                    padding: 0, 0, dp(3.5), 0
                    update_selected: root.update_selected
            BoxLayout:
                id: mapbox
                size_hint: .5, 1
                pos_hint: {'x': 1.2, 'y': 0}
                padding: dp(3.5), 0, 0, 0
                MapView:
                    id: map
                    background_color: 1, 1, 1, 1
        BoxLayout:
            id: buttom
            size_hint: 1, None
            height: self.minimum_height
            spacing: dp(7)
            GuiButton:
                id: back_button
                text: "Back"
                on_release: Clock.schedule_once(lambda dt: root.go_back())
            GuiButton:
                id: download_button
                text: "Download"
                disabled: len(root.download_list) == 0
                on_release: root.download()
""")


class FlightListScreen(Screen):
    map_marker = ObjectProperty(None)
    download_list = ListProperty([])

    def __init__(self, **kwargs):
        super(FlightListScreen, self).__init__(**kwargs)
        self.active_download_list = []

    def on_enter(self, **kwargs):
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
        self.manager.busy_progress(progress)
        if progress < 1.0:
            Clock.schedule_once(lambda dt: self.add_flights(flight_queue), .02)
        # add a button for the flight
        date_str = utc_to_local(flight.datetime).strftime("%A\n%d %b %Y\n%H:%M")
        self.ids.list_bl.add_widget(
            GuiSelsectButton(text=date_str, data=flight.num,
                             on_release=lambda x, n=flight.num:
                                 Clock.schedule_once(lambda dt: self.manager.download_flight_header(n))))

    def go_back(self, *largs):
        self.manager.current = 'ports'

    def show_map(self, flight_brief_header):
        shrink = animation.animate_size(.5, 1, use_hint=True, duration=.6)
        slide = animation.animate_pos(.5, 0, use_hint=True, duration=.6)
        shrink.start(self.ids.listbox)
        slide.start(self.ids.mapbox)

        map = self.ids.map
        marker = MapMarkerPopup(lat=flight_brief_header.latitude,
                                lon=flight_brief_header.longitude)
        map.add_marker(marker)
        if self.map_marker is not None:
            map.remove_marker(self.map_marker)
        self.map_marker = marker

    def on_map_marker(self, instance, marker):
        map = self.ids.map
        if marker is not None:
            map.center_on(marker.lat,
                          marker.lon)
            map.zoom = 13

    def update_selected(self, button, selected):
        if button in self.active_download_list:
            return
        if selected:
            self.download_list.append(button)
        else:
            self.download_list.remove(button)
        if self.download_list is None:
            self.download_list = []

    def download(self):
        for button in self.download_list:
            self.manager.download_flight(button.data)
            self.active_download_list.append(button)

    def unselect_flight(self, flight):
        for button in self.download_list:
            if button.data == flight:
                self.active_download_list.remove(button)
                button.selected = False
        if self.active_download_list is None:
            self.active_download_list = []


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
