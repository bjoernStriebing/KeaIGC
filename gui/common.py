from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty
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

    def on_touch_down(self, touch):
        # if self.collide_point(*touch.pos):
        #     self.set_background_color(self.background_down_color)
        super(GuiButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        # if self.collide_point(*touch.pos):
        # self.set_background_color(self.background_normal_color)
        super(GuiButton, self).on_touch_up(touch)

    def set_background_color(self, color):
        self.background_color = color


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
