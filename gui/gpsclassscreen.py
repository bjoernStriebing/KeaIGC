from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.metrics import *

from common import GuiLabel, GuiButton
import gpsdevice


Builder.load_string("""
<GpsClassScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        GuiLabel:
            id: header
            size_hint: 1, None
            height: dp(32)
            text: "Select your type of GPS device"
            font_size: dp(16)
            text_size: self.width - dp(18), self.height - dp(4)
            halign: 'left'
            valign: 'bottom'
            canvas.before:
                Color:
                    rgba: 245./255, 222./255, 84./255, 1
                Rectangle:
                    size: self.width, dp(3)
                    pos: self.x, self.y + dp(1)
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
            GuiButton:
                text: "Back"
                disabled: True
""")


class GpsClassScreen(Screen):

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
