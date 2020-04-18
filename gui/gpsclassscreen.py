from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from .common import GuiLabel, GuiButton, GuiGridLayout, GuiMetric
import gpsdevice


Builder.load_string("""
<GpsClassScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 12 * root.dp
        spacing: 7 * root.dp
        ScreenHeader:
            id: header
            text: "Select your type of GPS device"
        ScrollView:
            bar_width: 3
            scroll_distance: 20 * root.dp
            scroll_wheel_distance: 20 * root.dp
            smooth_scroll_end: 8
            GuiGridLayout:
                id: list_bl
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            id: buttom
            size_hint: 1, None
            height: self.minimum_height
            GuiButton:
                text: "Back"
                disabled: True
""")


class GpsClassScreen(Screen, GuiMetric):

    def on_pre_enter(self, **kwargs):
        super(GpsClassScreen, self).on_pre_enter(**kwargs)
        self.list_gps_classes()

    def list_gps_classes(self):
        self.ids.list_bl.clear_widgets()
        for device in gpsdevice.GpsDevices:
            name = device.get_class(device).GUI_NAME
            if name.startswith('gps'):
                name = name.replace('gps', '')
            self.ids.list_bl.add_widget(
                GuiButton(text=name,
                          on_release=lambda x: Clock.schedule_once(lambda dt: self.manager.device_selected(x, device))))
