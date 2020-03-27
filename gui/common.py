from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, NumericProperty
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
    pass


class GuiSelsectButton(GuiButton):
    selected = BooleanProperty(False)

    def on_press(self):
        self.selected ^= True  # toggle
        return super(GuiSelsectButton, self).on_press()

    def on_selected(self, instance, selected):
        if selected:
            self._bg_normal = self.background_normal
            self.background_normal = self.background_down
        else:
            self.background_normal = self._bg_normal


Builder.load_string("""
<GuiLabel>:
    size_hint: 1, None
    height: dp(60)
""")


class GuiLabel(Label, GuiColor):
    pass


Builder.load_string("""
<GuiGridLayout@GridLayout>:
    cols: 1
    spacing: dp(5)

""")

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
