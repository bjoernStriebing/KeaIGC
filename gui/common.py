from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty
from kivy.graphics import Rectangle, Color
from kivy.metrics import *

Builder.load_string("""
<GuiColor>
    bg_colour: 1, 1, 1, 1
    f_colour: .1, .1, 0.1, 1
    canvas.before:
        Color:
            rgba: self.bg_colour
        Rectangle:
            size: self.size
            pos: self.pos
    color: self.f_colour
""")


class GuiColor(Widget):
    pass


Builder.load_string("""
<GuiButton>:
    size_hint: 1, None
    height: dp(60)
    background_color: 1, 1, 1, 1
    background_normal: "gui/img/g85.png"
    background_down: "gui/img/highlightColour.png"
""")


class GuiButton(Button, GuiColor):
    data = ObjectProperty(None)
    pass


class GuiSelsectButton(GuiButton):
    selected = BooleanProperty(False)

    def on_press(self, *args):
        super(GuiSelsectButton, self).on_press()
        self.selected ^= True  # toggle

    def on_selected(self, instance, selected):
        if selected:
            self._bg_normal = self.background_normal
            self.background_normal = self.background_down
        else:
            self.background_normal = self._bg_normal
        try:
            self.parent.update_selected(self, selected)
        except AttributeError:
            pass


class GuiImgButton(ButtonBehavior, Image):

    def on_press(self):
        with self.canvas.before:
            Color(245./255, 222./255, 84./255, 1, mode='rgba')
            Rectangle(pos=self.pos, size=self.size)
        self._opacity = self.opacity
        self.opacity = 1

    def on_release(self):
        self.opacity = self._opacity
        self.canvas.before.clear()


Builder.load_string("""
<GuiLabel>:
    size_hint: 1, None
    height: dp(60)
    text_size: self.size
    halign: 'center'
    valign: 'middle'
""")


class GuiLabel(Label, GuiColor):
    pass


Builder.load_string("""
<GuiTextInput>:
    size_hint: 1, None
    height: dp(24)
    multiline: False
    background_normal: "gui/img/g85.png"
    background_active: "gui/img/g85.png"
    selection_color: 245./255, 222./255, 84./255, .62
    cursor_color: 1, 0, 0, 1
    write_tab: False
    text_validate_unfocus: False
""")


class GuiTextInput(TextInput):
    pass


Builder.load_string("""
<GuiGridLayout>:
    cols: 1
    spacing: dp(5)

""")


class GuiGridLayout(GridLayout):
    pass


Builder.load_string("""
<ScreenHeader@GuiLabel>:
    size_hint: 1, None
    height: dp(32)
    font_size: dp(16)
    text_size: self.width - dp(18), self.height - dp(4)
    halign: 'left'
    valign: 'bottom'
    canvas.before:
        Color:
            rgba: 245./255, 222./255, 84./255, 1
        Rectangle:
            group: 'bar'
            size: self.width, dp(3)
            pos: self.x, self.y + dp(1)
""")
