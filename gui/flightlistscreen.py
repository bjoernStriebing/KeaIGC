import os
# import pytz
import time
import Queue as queue
from datetime import datetime
# from tzlocal import get_localzone
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, ObjectProperty
from kivy.metrics import *

from common import GuiLabel, GuiButton, GuiSelsectButton, GuiTextInput
from library import utc_to_local
import gpsdevice
import animation
from contrib.gardenmapview import MapView, MapMarkerPopup

# local_tz = get_localzone()

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
                spacing: dp(7)
                orientation: 'vertical'
                MapView:
                    id: map
                    background_color: 1, 1, 1, 1
                BoxLayout:
                    spacing: dp(7)
                    orientation: 'vertical'
                    height: self.minimum_height
                    size_hint_y: None

                    BoxLayout:
                        orientation: 'vertical'
                        height: self.minimum_height
                        size_hint_y: None
                        spacing: dp(3)
                        GuiLabel:
                            height: dp(20)
                            text: "Takeoff Altitude"
                            canvas.before:
                                Color:
                                    rgba: 245./255, 222./255, 84./255, 1
                                Rectangle:
                                    size: self.width, dp(1)
                                    pos: self.x, self.y + dp(1)
                        BoxLayout:
                            spacing: dp(7)
                            orientation: 'vertical'
                            height: self.minimum_height
                            size_hint_y: None
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                GuiLabel:
                                    height: dp(20)
                                    text: "Barometer"
                                GuiLabel:
                                    height: dp(20)
                                    text: "GPS"
                                GuiLabel:
                                    height: dp(20)
                                    text: "Offset"
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                GuiLabel:
                                    id: baro_alt
                                    height: dp(20)
                                GuiLabel:
                                    id: gps_alt
                                    height: dp(20)
                                GuiLabel:
                                    id: offset_alt
                                    height: dp(20)

                    BoxLayout:
                        orientation: 'vertical'
                        height: self.minimum_height
                        size_hint_y: None
                        spacing: dp(3)
                        GuiLabel:
                            height: dp(20)
                            text: "Metadata"
                            canvas.before:
                                Color:
                                    rgba: 245./255, 222./255, 84./255, 1
                                Rectangle:
                                    size: self.width, dp(1)
                                    pos: self.x, self.y + dp(1)
                        BoxLayout:
                            spacing: dp(7)
                            orientation: 'vertical'
                            height: self.minimum_height
                            size_hint_y: None
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                spacing: dp(7)
                                GuiLabel:
                                    text: "Pilot"
                                    height: dp(24)
                                    halign: 'left'
                                    size: dp(100), dp(24)
                                    size_hint: None, None
                                GuiTextInput:
                                    id: pilot_name
                                    height: dp(24)
                                    on_focus:
                                        if self.focus: replace_pilot.selected = True
                                GuiSelsectButton:
                                    id: replace_pilot
                                    text: "Replace"
                                    size: dp(62), dp(24)
                                    size_hint: None, None
                                    on_selected: root.pilot_overwrite(self.selected)
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                spacing: dp(7)
                                GuiLabel:
                                    text: "Glider"
                                    height: dp(24)
                                    halign: 'left'
                                    size: dp(100), dp(24)
                                    size_hint: None, None
                                GuiTextInput:
                                    id: glider_name
                                    height: dp(24)
                                    on_focus:
                                        if self.focus: replace_glider.selected = True
                                GuiSelsectButton:
                                    id: replace_glider
                                    text: "Replace"
                                    size: dp(62), dp(24)
                                    size_hint: None, None
                                    on_selected: root.glider_overwrite(self.selected)

                    BoxLayout:
                        orientation: 'vertical'
                        height: self.minimum_height
                        size_hint_y: None
                        spacing: dp(3)
                        GuiLabel:
                            height: dp(20)
                            text: "Export"
                            canvas.before:
                                Color:
                                    rgba: 245./255, 222./255, 84./255, 1
                                Rectangle:
                                    size: self.width, dp(1)
                                    pos: self.x, self.y + dp(1)
                        BoxLayout:
                            height: self.minimum_height
                            size_hint_y: None
                            spacing: dp(7)
                            GuiLabel:
                                size: dp(100), dp(60)
                                size_hint: None, None
                                text: "Export Path"
                                halign: 'left'
                            GuiButton:
                                id: export_path
                                height: dp(60)
                                text: '~/Desktop'
                                on_press:
                                    self.text = '~/Desktop'
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
        Window.bind(on_dropfile=self._on_file_drop)
        self.active_download_list = []
        self._last_press = [0, None]

    def on_enter(self, **kwargs):
        super(FlightListScreen, self).on_pre_enter(**kwargs)
        self.list_flights()
        self.fill_meta()

    def list_flights(self):
        self.ids.list_bl.clear_widgets()
        self.manager.gps.get_list()

    def fill_meta(self):
        gps = self.manager.gps.gps
        self.ids.pilot_name.text = str(gps.pilot_name)
        self.ids.replace_pilot.selected = True

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
        button = GuiSelsectButton(text=date_str, data={'num': flight.num})
        button.bind(on_release=lambda x, n=flight.num:
                    Clock.schedule_once(lambda dt: self.manager.download_flight_header(n)))
        button.bind(on_press=lambda x: self.select_one(x))
        self.ids.list_bl.add_widget(button)

    def go_back(self, *largs):
        self.manager.current = 'ports'

    @mainthread
    def show_map(self, flight_num, flight_brief_header):
        # add header data to button
        for button in self.ids.list_bl.children:
            try:
                if button.data['num'] == flight_num:
                    button.data['header'] = flight_brief_header
            except KeyError:
                continue

        # move in the map display
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
        self.ids.baro_alt.text = '{} m'.format(flight_brief_header.altitude_baro)
        self.ids.gps_alt.text = '{} m'.format(flight_brief_header.altitude_gps)
        self.ids.offset_alt.text = '{} m'.format(flight_brief_header.altitude_baro
                                                 - flight_brief_header.altitude_gps)
        if not self.ids.replace_pilot.selected:
            self.ids.pilot_name.text = flight_brief_header.pilot_name
        if not self.ids.replace_glider.selected:
            self.ids.glider_name.text = flight_brief_header.glider_name

    def on_map_marker(self, instance, marker, *args, **kwargs):
        map = self.ids.map
        if marker is not None:
            map.center_on(marker.lat,
                          marker.lon)
            map.zoom = 13

    def update_selected(self, button, selected):
        if selected:
            if button in self.active_download_list:
                return
            self.download_list.append(button)
        else:
            try:
                self.download_list.remove(button)
            except ValueError:
                pass
        if self.download_list is None:
            self.download_list = []

    def download(self):
        output_dir = os.path.expanduser(self.ids.export_path.text)
        for button in self.download_list:
            try:
                timestamp = utc_to_local(button.data['header'].timestamp)
            except KeyError:
                # FIXME log a warning
                timestamp = utc_to_local(datetime.utcnow())
            filename = '{}.igc'.format(timestamp.strftime('%a %d-%b-%Y %H-%M'))
            output_file = os.path.join(output_dir, filename)
            self.manager.download_flight(button.data['num'], output_file)
            self.active_download_list.append(button)

    def unselect_flight(self, flight):
        for button in self.download_list:
            if button.data['num'] == flight:
                self.active_download_list.remove(button)
                button.selected = False
        if self.active_download_list is None:
            self.active_download_list = []

    def select_one(self, button):
        now = time.time()
        if now - self._last_press[0] < 0.5 and button == self._last_press[1]:
            for b in self.ids.list_bl.children:
                b.selected = False
            # actually don't select the button, it will happen on_release
            # button.selected = True
            self.download_list = []
        self._last_press = [now, button]

    def pilot_overwrite(self, selected):
        if selected:
            self.manager.gps.set_pilot_overwrite(overwrite=self.ids.pilot_name.text)
        else:
            self.manager.gps.set_pilot_overwrite(overwrite=False)

    def glider_overwrite(self, selected):
        if selected:
            self.manager.gps.set_glider_overwrite(overwrite=self.ids.glider_name.text)
        else:
            self.manager.gps.set_glider_overwrite(overwrite=False)

    def _on_file_drop(self, window, file_path):
        path = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        home_path = os.path.expanduser('~')
        path = path.replace(home_path, '~')
        self.ids.export_path.text = path


# def utc_to_local(utc_dt):
#     return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
