from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty

import gpsdevice


Builder.load_string("""
<MessagePopup>:
    size_hint: .9, .4
    pos_hint: {'x': (1 - self.size_hint_x) / 2, 'y': (1 - self.size_hint_y) / 2}
    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.message
        Button:
            text: 'OK'
            on_release: root.dismiss()
""")


class MessagePopup(Popup):
    message = StringProperty("")
    caller = ObjectProperty(None)
    auto_dismiss = BooleanProperty(False)

    def __init__(self, message, **kwargs):
        self.message = message
        super(MessagePopup, self).__init__(**kwargs)
        self.open()
