from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty

from .common import ThemePopup
import gpsdevice


Builder.load_string("""
<MessagePopup>:
    size_hint: .9, .45
    pos_hint: {'x': (1 - self.size_hint_x) / 2, 'y': (1 - self.size_hint_y) / 2}
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        GuiLabel:
            text: root.message
            size_hint_y: 1
        GuiButton:
            text: 'OK'
            on_release: root.dismiss()
""")


class MessagePopup(ThemePopup):
    message = StringProperty("")
    caller = ObjectProperty(None)
    auto_dismiss = BooleanProperty(False)

    def __init__(self, message, **kwargs):
        self.message = message
        super(MessagePopup, self).__init__(**kwargs)
        self.open()
