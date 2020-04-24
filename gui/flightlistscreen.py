import os
import time
import queue
from datetime import datetime
from kivy.lang import Builder
from kivy.config import Config
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, ObjectProperty

from .common import GuiLabel, GuiButton, GuiSelsectButton, GuiContainerSelectButton, GuiTextInput, GuiGridLayout, GuiMetric
from .settingsscreen import SettingsScreen
from .contrib.gardenmapview import MapView, MapMarkerPopup
from . import animation
from library import utc_to_local
import gpsdevice


Builder.load_string("""
<FlightListScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 12 * root.dp
        spacing: 7 * root.dp
        ScreenHeader:
            id: header
            text: "Select flights from list below"
        FloatLayout:
            ScrollView:
                id: listbox
                size_hint: 1, 1
                pos_hint: {'x': 0, 'y': 0}
                bar_width: 3
                scroll_distance: 20 * root.dp
                scroll_wheel_distance: 20 * root.dp
                smooth_scroll_end: 8
                GuiGridLayout:
                    id: list_bl
                    size_hint_y: None
                    height: self.minimum_height
                    padding: 0, 0, 3.5 * self.dp, 0
                    update_selected: root.update_selected
            BoxLayout:
                id: mapbox
                size_hint: .5, 1
                pos_hint: {'x': 1.2, 'y': 0}
                padding: 3.5 * root.dp, 0, 0, 0
                spacing: 7 * root.dp
                orientation: 'vertical'
                MapView:
                    id: map
                    background_color: 1, 1, 1, 1
                BoxLayout:
                    spacing: 7 * root.dp
                    orientation: 'vertical'
                    height: self.minimum_height
                    size_hint_y: None

                    BoxLayout:
                        orientation: 'vertical'
                        height: self.minimum_height
                        size_hint_y: None
                        spacing: 3 * root.dp
                        GuiLabel:
                            height: 20 * self.dp
                            text: "Takeoff Altitude"
                            canvas.before:
                                Color:
                                    rgba: 245./255, 222./255, 84./255, 1
                                Rectangle:
                                    size: self.width, 1 * self.dp
                                    pos: self.x, self.y + 1 * self.dp
                        BoxLayout:
                            spacing: 7 * root.dp
                            orientation: 'vertical'
                            height: self.minimum_height
                            size_hint_y: None
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                GuiLabel:
                                    height: 20 * self.dp
                                    text: "Barometer"
                                GuiLabel:
                                    height: 20 * self.dp
                                    text: "GPS"
                                GuiLabel:
                                    height: 20 * self.dp
                                    text: "Offset"
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                GuiLabel:
                                    id: baro_alt
                                    height: 20 * self.dp
                                GuiLabel:
                                    id: gps_alt
                                    height: 20 * self.dp
                                GuiLabel:
                                    id: offset_alt
                                    height: 20 * self.dp

                    BoxLayout:
                        orientation: 'vertical'
                        height: self.minimum_height
                        size_hint_y: None
                        spacing: 3 * root.dp
                        GuiLabel:
                            height: 20 * self.dp
                            text: "Metadata"
                            canvas.before:
                                Color:
                                    rgba: 245./255, 222./255, 84./255, 1
                                Rectangle:
                                    size: self.width, 1 * self.dp
                                    pos: self.x, self.y + 1 * self.dp
                        BoxLayout:
                            spacing: 7 * root.dp
                            orientation: 'vertical'
                            height: self.minimum_height
                            size_hint_y: None
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                spacing: 7 * root.dp
                                GuiLabel:
                                    text: "Pilot"
                                    height: 24 * self.dp
                                    halign: 'left'
                                    size: 100 * self.dp, 24 * self.dp
                                    size_hint: None, None
                                GuiTextInput:
                                    id: pilot_name
                                    height: 24 * self.dp
                                    on_focus:
                                        if self.focus: replace_pilot.selected = True
                                GuiSelsectButton:
                                    id: replace_pilot
                                    text: "Replace"
                                    size: 62 * self.dp, 24 * self.dp
                                    size_hint: None, None
                                    on_selected: root.pilot_overwrite(self.selected)
                            BoxLayout:
                                height: self.minimum_height
                                size_hint_y: None
                                spacing: 7 * root.dp
                                GuiLabel:
                                    text: "Glider"
                                    height: 24 * self.dp
                                    halign: 'left'
                                    size: 100 * self.dp, 24 * self.dp
                                    size_hint: None, None
                                GuiTextInput:
                                    id: glider_name
                                    height: 24 * self.dp
                                    on_focus:
                                        if self.focus: replace_glider.selected = True
                                GuiSelsectButton:
                                    id: replace_glider
                                    text: "Replace"
                                    size: 62 * self.dp, 24 * self.dp
                                    size_hint: None, None
                                    on_selected: root.glider_overwrite(self.selected)

                    BoxLayout:
                        orientation: 'vertical'
                        height: self.minimum_height
                        size_hint_y: None
                        spacing: 3 * root.dp
                        GuiLabel:
                            height: 20 * self.dp
                            text: "Export"
                            canvas.before:
                                Color:
                                    rgba: 245./255, 222./255, 84./255, 1
                                Rectangle:
                                    size: self.width, 1 * self.dp
                                    pos: self.x, self.y + 1 * self.dp
                        BoxLayout:
                            height: self.minimum_height
                            size_hint_y: None
                            spacing: 7 * root.dp
                            GuiLabel:
                                size: 100 * self.dp, 60 * self.dp
                                size_hint: None, None
                                text: "Export Path"
                                halign: 'left'
                            GuiButton:
                                id: export_path
                                height: 60 * self.dp
                                text: '~/Desktop'
                                on_press:
                                    self.text = '~/Desktop'
        BoxLayout:
            id: buttom
            size_hint: 1, None
            height: self.minimum_height
            spacing: 7 * root.dp
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


class FlightListScreen(Screen, GuiMetric):
    map_marker = ObjectProperty(None)
    download_list = ListProperty([])

    def __init__(self, **kwargs):
        super(FlightListScreen, self).__init__(**kwargs)
        Window.bind(on_dropfile=self._on_file_drop)
        self.active_download_list = []
        self._last_press = [0, None]
        self._clear_cb_set = False

    def on_parent(self, *args):
        default_pilot = Config.get('user', 'pilot_name')
        default_wing = Config.get('user', 'wing_name')
        if default_pilot:
            self.ids.pilot_name.text = default_pilot.strip()
            self.ids.replace_pilot.selected = True
        if default_wing:
            self.ids.glider_name.text = default_wing.strip()
            self.ids.replace_glider.selected = True

    def on_enter(self, **kwargs):
        super(FlightListScreen, self).on_pre_enter(**kwargs)
        if isinstance(self.manager.last_screen, SettingsScreen):
            return
        self.list_flights()
        self.fill_meta()
        if not self._clear_cb_set:
            self.manager.bind(current_screen=lambda _, s: self.clear(screen=s))
            self._clear_cb_set = True

    def list_flights(self):
        self.ids.list_bl.clear_widgets()
        self.manager.gps.get_list()

    def fill_meta(self):
        gps = self.manager.gps.gps
        if not Config.get('user', 'pilot_name'):
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
        flightdate = utc_to_local(flight.datetime)
        button = GuiContainerSelectButton(data={'num': flight.num})
        button.bind(on_release=lambda x, n=flight.num:
                    Clock.schedule_once(lambda dt: self.manager.download_flight_header(n)))
        button.bind(on_press=lambda x: self.select_one(x))

        button.add_widget(GuiLabel(text=flightdate.strftime("%d %b %Y\n%A"),
                                   size_hint=(.31, 1),
                                   pos_hint={'x': 0.02, 'y': 0},
                                   bg_colour=(1, 1, 1, 0),
                                   halign='left'))
        button.add_widget(GuiLabel(text=flightdate.strftime("%H:%M"),
                                   size_hint=(.34, 1),
                                   pos_hint={'x': .33, 'y': 0},
                                   bg_colour=(1, 1, 1, 0),
                                   halign='center'))
        button.add_widget(GuiLabel(text=str(flight.duration),
                                   size_hint=(.31, 1),
                                   pos_hint={'x': .67, 'y': 0},
                                   bg_colour=(1, 1, 1, 0),
                                   halign='right'))
        self.ids.list_bl.add_widget(button)

    def go_back(self, *largs):
        try:
            auto_detect_ports = Config.getboolean('user', 'auto_detect_ports')
        except ValueError:
            auto_detect_ports = False
        if auto_detect_ports:
            self.manager.current = 'devices'
        else:
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
            self.ids.pilot_name.text = flight_brief_header.pilot_name.strip()
        if not self.ids.replace_glider.selected:
            self.ids.glider_name.text = flight_brief_header.glider_name.strip()

    def on_map_marker(self, instance, marker, *args, **kwargs):
        map = self.ids.map
        if marker is not None:
            map.center_on(marker.lat,
                          marker.lon)
            map.zoom = 14

    def update_selected(self, button, selected):
        if button in self.active_download_list:
            return
        if selected:
            if button not in self.download_list:
                self.download_list.append(button)
        else:
            try:
                self.download_list.remove(button)
            except ValueError:
                pass

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
            if button not in self.download_list:
                self.active_download_list.append(button)

    def unselect_flight(self, flight):
        for button in self.download_list:
            if button.data['num'] == flight:
                self.download_list.remove(button)
                button.selected = False
                break
        try:
            self.active_download_list.remove(button)
        except ValueError:
            pass

    def select_one(self, button):
        now = time.time()
        if now - self._last_press[0] < 0.5 and button == self._last_press[1]:
            for b in self.ids.list_bl.children:
                b.selected = False
            # actually don't select the button, it will happen on_release
            # button.selected = True
            self.download_list = self.active_download_list
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

    def clear(self, screen=None):
        if screen is not self and not isinstance(screen, SettingsScreen):
            self.download_list = []
            self.active_download_list = []
            self.ids.list_bl.clear_widgets()

    def _on_file_drop(self, window, file_path):
        path = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        path = path.decode()
        home_path = os.path.expanduser('~')
        path = path.replace(home_path, '~')
        self.ids.export_path.text = path
