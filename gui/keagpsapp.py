import os
from glob import glob
from serial import SerialException
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from gpsclassscreen import GpsClassScreen
from serialscreen import SerialScreen
from flightlistscreen import FlightListScreen
from popups.message import MessagePopup

from common import GuiColor


class KeaGpsDownloader(ScreenManager, GuiColor):

    def __init__(self, **kwargs):
        super(KeaGpsDownloader, self).__init__(**kwargs)
        self.device_screen = GpsClassScreen(name='devices')
        self.serial_screen = SerialScreen(name='ports')
        self.flightlist_screen = FlightListScreen(name='flightlist')
        self.add_widget(self.device_screen)
        self.add_widget(self.serial_screen)
        self.add_widget(self.flightlist_screen)
        self.current = 'devices'

    def device_selected(self, button, device):
        self.gps = device.get_class(device)(port=None)
        self.current = 'ports'

    def port_selected(self, button, port):
        print button.text, port
        try:
            self.gps.io = port
        except (SerialException, AttributeError, ValueError):
            button.disabled = True
            MessagePopup('Serial port "{}" does not match GPS device {}'.format(
                port, self.gps.__class__.GUI_NAME), caller=self)
            return
        self.current = 'flightlist'


class KeaGpsApp(App):

    def build(self):
        self.gui = KeaGpsDownloader()
        return self.gui


if __name__ == '__main__':
    KeaPgApp().run()
