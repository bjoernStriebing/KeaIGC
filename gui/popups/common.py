import os
from PIL import Image, ImageFilter
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.graphics.opengl import glReadPixels, GL_RGB, GL_UNSIGNED_BYTE
from kivy.properties import ListProperty, StringProperty, BooleanProperty, ObjectProperty, OptionProperty
from kivy.uix.popup import PopupException
from kivy.uix.modalview import ModalView
from kivy.uix.widget import WidgetException
from kivy.uix.gridlayout import GridLayout

from ..common import GuiColor, GuiMetric
from ..metrics import metric


@mainthread
def _blur_popup_bg():
    background_window = App.get_running_app().root_widget
    blur_effect = background_window.blur_effect
    width, height = Window.size
    screenbuffer = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    screenimg = Image.frombytes('RGB', (width, height), screenbuffer)
    screenblur = screenimg.filter(ImageFilter.GaussianBlur(4 * metric.dp))
    try:
        if blur_effect.texture.width != width or blur_effect.texture.height != height:
            blur_effect.texture = Texture.create(size=(width, height))
    except AttributeError:
        blur_effect.texture = Texture.create(size=(width, height))
    blur_effect.texture.blit_buffer(screenblur.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
    try:
        background_window.add_widget(blur_effect)
    except WidgetException:
        pass


Builder.load_string("""
<ThemePopup>:
    _container: container
    GridLayout:
        cols: 1
        pos: root.pos
        size: root.size
        spacing: 5 * root.dp
        padding: 12 * root.dp

        ScreenHeader:
            text: root.title

        BoxLayout:
            id: container
            padding: -12 * root.dp
""")


class ThemePopup(ModalView, GuiColor, GuiMetric):
    title = StringProperty('Popup')
    background = StringProperty(os.path.join('gui', 'img', 'popup_bg.png'))
    auto_dismiss = BooleanProperty(False)

    content = ObjectProperty(None)
    _container = ObjectProperty(None)

    def __init__(self, **kwargs):
        _blur_popup_bg()
        self.title_color = GuiColor().f_colour
        self.background_color = GuiColor().bg_colour[:-1] + [.2]
        ModalView.__init__(self, **kwargs)

    def add_widget(self, widget):
        if self._container:
            if self.content:
                raise PopupException(
                    'Popup can have only one widget as content')
            self.content = widget
        else:
            super(ThemePopup, self).add_widget(widget)

    def on_content(self, instance, value):
        if self._container:
            self._container.clear_widgets()
            self._container.add_widget(value)

    def on__container(self, instance, value):
        if value is None or self.content is None:
            return
        self._container.clear_widgets()
        self._container.add_widget(self.content)

    def on_dismiss(self):
        super(ThemePopup, self).on_dismiss()
        background_window = App.get_running_app().root_widget
        background_window.remove_widget(background_window.blur_effect)
