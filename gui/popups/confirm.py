from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty

from .common import ThemePopup
import gpsdevice


Builder.load_string("""
<ConfirmPopup>:
    size_hint: .9, .6
    pos_hint: {'x': (1 - self.size_hint_x) / 2, 'y': (1 - self.size_hint_y) / 2}
    background: ''
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        GuiLabel:
            text: root.message
            size_hint_y: 1
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(7)
            GuiButton:
                text: 'No'
                on_release: root.dismiss()
            GuiButton:
                text: 'OK'
                on_release: root.carry_on()
""")


class ConfirmPopup(ThemePopup):
    message = StringProperty("")
    caller = ObjectProperty(None)
    auto_dismiss = BooleanProperty(False)
    ok_callback = ObjectProperty(None)

    def __init__(self, message, **kwargs):
        self.message = message
        super(ConfirmPopup, self).__init__(**kwargs)
        self.open()

    def carry_on(self):
        try:
            self.ok_callback()
        except TypeError:
            pass
        finally:
            self.dismiss()
