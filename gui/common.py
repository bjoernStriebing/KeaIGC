from kivy.lang import Builder
from kivy.event import EventDispatcher
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty
from kivy.graphics import Rectangle, Color
from .metrics import metric


class GuiMetric(EventDispatcher):
    dp = NumericProperty(metric.dp)

    def __init__(self, **kwargs):
        super(GuiMetric, self).__init__(**kwargs)
        metric.bind(dp=lambda _, dp: self.property('dp').set(self, dp))


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
    height: 60 * self.dp
    font_size: 15 * self.dp
    background_color: 1, 1, 1, 1
    background_normal: "gui/img/g85.png"
    background_down: "gui/img/highlightColour.png"
""")


class GuiButton(Button, GuiColor, GuiMetric):
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


Builder.load_string("""
<-GuiContainerButton>:
    size_hint: 1, None
    height: 60 * self.dp
    background_normal: "gui/img/g85.png"
    background_down: "gui/img/highlightColour.png"
    Image:
        size: root.size
        pos_hint: {'x': 0, 'y': 0}
        source: root.background_normal if root.state == 'normal' else root.background_down
        allow_stretch: True
        keep_ratio: False
""")


class GuiContainerButton(ButtonBehavior, FloatLayout, GuiMetric):
    data = ObjectProperty(None)


class GuiContainerSelectButton(GuiContainerButton, GuiSelsectButton):
    pass


class GuiImgButton(ButtonBehavior, Image, GuiMetric):

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
    font_size: 15 * self.dp
    height: 60 * self.dp
    text_size: self.size
    halign: 'center'
    valign: 'middle'
""")


class GuiLabel(Label, GuiColor, GuiMetric):
    pass


Builder.load_string("""
<GuiSwitch>:
    active_norm_pos: max(0., min(1., (int(self.active) + self.touch_distance / (41 * self.dp))))
    canvas:
        Color:
            rgb: 1, 1, 1
        Rectangle:
            source: 'atlas://data/images/defaulttheme/switch-background'
            size: 83 * self.dp, 32 * self.dp
            pos: int(self.center_x - 41 * self.dp), int(self.center_y - 16 * self.dp)
        Rectangle:
            source: 'atlas://data/images/defaulttheme/switch-button'
            size: 43 * self.dp, 32 * self.dp
            pos: int(self.center_x - 41 * self.dp + self.active_norm_pos * 41 * self.dp), int(self.center_y - 16 * self.dp)
""")


class GuiSwitch(Switch, GuiMetric):
    pass


Builder.load_string("""
<GuiTextInput>:
    size_hint: 1, None
    height: 24 * self.dp
    font_size: 15 * self.dp
    multiline: False
    background_normal: "gui/img/g85.png"
    background_active: "gui/img/g85.png"
    selection_color: 245./255, 222./255, 84./255, .62
    cursor_color: 1, 0, 0, 1
    write_tab: False
    text_validate_unfocus: False
""")


class GuiTextInput(TextInput, GuiMetric):
    pass


Builder.load_string("""
<GuiGridLayout>:
    cols: 1
    spacing: 5 * self.dp

""")


class GuiGridLayout(GridLayout, GuiMetric):
    pass


Builder.load_string("""
<ScreenHeader@GuiLabel>:
    size_hint: 1, None
    height: 32 * self.dp
    font_size: 16 * self.dp
    text_size: self.width - 18 * self.dp, self.height - 4 * self.dp
    halign: 'left'
    valign: 'bottom'
    canvas.before:
        Color:
            rgba: 245./255, 222./255, 84./255, 1
        Rectangle:
            group: 'bar'
            size: self.width, 3 * self.dp
            pos: self.x, self.y + 1 * self.dp
""")
