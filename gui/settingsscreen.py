import json
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import Settings, SettingsPanel, SettingsWithNoMenu, InterfaceWithNoMenu
from kivy.uix.settings import SettingItem, SettingBoolean, SettingTitle
from kivy.properties import ObjectProperty, StringProperty
from kivy.config import Config, ConfigParser

from .common import GuiLabel, GuiButton, GuiSwitch, GuiGridLayout, GuiMetric
from .popups.message import MessagePopup
import gpsdevice


Builder.load_string("""
<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 12 * root.dp
        spacing: 12 * root.dp
        ScreenHeader:
            id: header
            text: "Settings"
        BoxLayout:
            id: settings_box
        BoxLayout:
            id: buttom
            size_hint: 1, None
            height: self.minimum_height
            GuiButton:
                text: "Close"
                on_release: root.close()
""")


class SettingsScreen(Screen, GuiMetric):

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        settings = GuiSettings()
        settings.add_json_panel(
            'Device Connection', Config,
            data="""
            [
                {
                    "type": "bool",
                    "title": "Serial port auto-detect",
                    "desc": "Talk to evry available serial port to find GPS device automatically",
                    "section": "user",
                    "key": "auto_detect_ports"
                },
                {
                    "type": "title",
                    "title": "IGC Header Overwrite Settings"
                },
                {
                    "type": "string",
                    "title": "Default pilot name",
                    "desc": "Overwrite pilot name reported by GPS. Leave blank to disable.",
                    "section": "user",
                    "key": "pilot_name"
                },
                {
                    "type": "string",
                    "title": "Default glider name",
                    "desc": "Overwrite glider name reported by GPS. Leave blank to disable.",
                    "section": "user",
                    "key": "wing_name"
                }
            ]
            """)
        self.ids.settings_box.add_widget(settings)
        self._settings = settings

    def close(self):
        for setting in self._settings.interface.current_panel.children:
            try:
                setting._validate(setting)
            except AttributeError:
                continue

        try:
            Config.write()
        except IOError as e:
            MessagePopup('Could not save settings due to an error:\n{}'.format(e))
        self.manager.current = self.manager.last_screen.name


Builder.load_string("""
<-GuiSettings>:
""")


class GuiSettings(SettingsWithNoMenu):
    def __init__(self, *args, **kwargs):
        self.interface_cls = InterfaceWithNoMenu
        self._types = {}
        super(Settings, self).__init__(*args, **kwargs)
        self.add_interface()
        self.register_type('string', GuiSettingString)
        self.register_type('bool', GuiSettingBoolean)
        # self.register_type('numeric', SettingNumeric)
        # self.register_type('options', SettingOptions)
        self.register_type('title', GuiSettingTitle)
        # self.register_type('path', SettingPath)

    def create_json_panel(self, title, config, filename=None, data=None):
        '''Create new :class:`SettingsPanel`.
        .. versionadded:: 1.5.0
        Check the documentation of :meth:`add_json_panel` for more information.
        '''
        if filename is None and data is None:
            raise Exception('You must specify either the filename or data')
        if filename is not None:
            with open(filename, 'r') as fd:
                data = json.loads(fd.read())
        else:
            data = json.loads(data)
        if type(data) != list:
            raise ValueError('The first element must be a list')
        panel = GuiSettingsPanel(title=title, settings=self, config=config)

        for setting in data:
            # determine the type and the class to use
            if 'type' not in setting:
                raise ValueError('One setting are missing the "type" element')
            ttype = setting['type']
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError(
                    'No class registered to handle the <%s> type' %
                    setting['type'])

            # create a instance of the class, without the type attribute
            del setting['type']
            str_settings = {}
            for key, item in setting.items():
                str_settings[str(key)] = item

            instance = cls(panel=panel, **str_settings)

            # instance created, add to the panel
            panel.add_widget(instance)

        return panel


Builder.load_string("""
<-GuiSettingsPanel>:
    spacing: 4 * self.dp
    padding: 0
    size_hint_y: None
    height: self.minimum_height

    GuiLabel:
        text: root.title
        valign: "bottom"
        height: 28 * self.dp
        font_size: 15 * self.dp

        canvas.before:
            Color:
                rgb: 1245./255, 222./255, 84./255, 1
            Rectangle:
                pos: self.x, self.y - 2 * self.dp
                size: self.width, min(int(.5 * self.dp), 1)

<-GuiSettingItem>:
    size_hint: .25, None
    height: labellayout.texture_size[1] + 10 * self.dp
    content: content
    canvas:
        Color:
            rgba: 1245./255, 222./255, 84./255, self.selected_alpha
        Rectangle:
            pos: self.x, self.y
            size: self.size

    BoxLayout:
        pos: root.pos

        Label:
            size_hint_x: .7
            id: labellayout
            markup: True
            color: .1, .1, 0.1, 1
            text: '{t}{n}[size={s}][color=777777]{d}[/color][/size]'.format(t=root.title or '', d=root.desc or '',s=14 * root.dp, n=chr(10))
            text_size: self.width - 16 * root.dp, None
            font_size: 15 * root.dp

        BoxLayout:
            id: content
            size_hint_x: .3


<GuiSettingTitle>:
    valign: "bottom"
    # size_hint: 1, None
    height: 28 * self.dp
    # font_size: 15 * self.dp
    text_size: self.size
    # color: .1, .1, .1, 1

    canvas.before:
        Color:
            rgb: 1245./255, 222./255, 84./255, 1
        Rectangle:
            pos: self.x, self.y - 2 * self.dp
            size: self.width, min(int(.5 * self.dp), 1)

<GuiSettingBoolean>:
    GuiSwitch:
        text: 'Boolean'
        pos: root.pos
        active: bool(root.values.index(root.value)) if root.value in root.values else False
        on_active: root.value = root.values[int(args[1])]

<GuiSettingString>:
    GuiTextInput:
        id: textinput
        text: root.value or ''
        pos_hint: {'right': 1, 'center_y': .5}
        # pos: root.pos
        on_text_validate: root._validate(self)
        on_focus: root._validate(self) if not self.focus else None


""")


class GuiSettingsPanel(SettingsPanel, GuiMetric):
    pass


class GuiSettingItem(SettingItem, GuiMetric):
    pass


class GuiSettingTitle(GuiLabel):
    panel = ObjectProperty(None)
    title = GuiLabel.text


class GuiSettingBoolean(GuiSettingItem, SettingBoolean):
    pass


class GuiSettingString(GuiSettingItem):

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', lambda x: self._focus())

    def _validate(self, instance):
        value = self.ids.textinput.text.strip()
        self.value = value

    def _focus(self):
        self.ids.textinput.focus = True
