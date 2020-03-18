import Queue as queue
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.metrics import *

from common import GuiLabel, GuiButton
import gpsdevice


Builder.load_string("""
<FlightListScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(7)
        GuiLabel:
            size_hint: 1, None
            height: dp(60)
            text: "Select flights from list below"
        GuiGridLayout:
            id: list_bl
        BoxLayout:
            id: buttom
            size_hint: 1, None
            height: self.minimum_height
            GuiButton:
                text: "Back"
                on_release: Clock.schedule_once(lambda dt: root.go_back())
""")


class FlightListScreen(Screen):

    def on_pre_enter(self, **kwargs):
        super(FlightListScreen, self).on_pre_enter(**kwargs)
        Clock.schedule_once(lambda dt: self.list_flights())

    def list_flights(self):
        self.ids.list_bl.clear_widgets()
        self.flight_queue = queue.Queue()
        self.manager.gps.get_list(result_queue=self.flight_queue)
        self.polling = Clock.schedule_interval(lambda dt: self.add_flight(), .02)
        # tracklist = self.manager.gps.tracklist
        # for t in tracklist:
        #     self.ids.list_bl.add_widget(GuiButton(text=str(t)))

    def add_flight(self):
        try:
            progress, flight = self.flight_queue.get_nowait()
        except queue.Empty:
            return
        if progress >= 1.0:
            self.polling.cancel()
        self.ids.list_bl.add_widget(GuiButton(text=str(flight)))

    def go_back(self, *largs):
        self.manager.current = 'ports'
