from dotenv import dotenv_values
from obswebsocket import obsws, requests
import datetime
import asyncio
from astral.sun import sun
from app_logger import LOGGER as log
from location import SEGUIN, format_time, get_tzinfo
from exceptions import SourceNameNotFound


class OBSWebSocketManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OBSWebSocketManager, cls).__new__(cls)
            cls.instance.__config = dotenv_values()
        return cls.instance
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __init__(self):
        if not self.isConnected():
            self.connect()
    
    def isConnected(self):
        if (hasattr(self, 'ws') and self.ws is not None):
            return True
        return False

    def connect(self):
        if self.isConnected():
            return
        obs_host = self.__config.get("obs_host", "localhost")
        obs_port = self.__config.get("obs_port", 4444)
        obs_password = self.__config.get("obs_password", "secret")
        self.ws = obsws(obs_host, obs_port, obs_password)
        self.ws.connect()
    
    def disconnect(self):
        if self.isConnected():
            self.ws.disconnect()

class OBSManager(OBSWebSocketManager):  
    day_sources = ["brooder", "birdpole", "chicken"]
    night_sources = ["brooder"]

    def __init__(self):
        super().__init__()
        if not hasattr(self, "sun_data"):
            self.set_today_events()
        if not hasattr(self, "sources"):
            self.set_scene_time()

    def setScene(self, scene_name, source_name, source_type="cam"):
        if source_name not in self.sources:
            raise SourceNameNotFound
        for source in self.sources:
            is_target = False
            if source == source_name:
                is_target = True
            r = requests.SetSceneItemRender(f"_{source}{source_type}", is_target, scene_name=scene_name)
            self.ws.call(r)
    
    def setAudioForMain(self, source_name):
        if source_name not in self.sources:
            raise SourceNameNotFound
        for source in self.sources:
            is_muted = True
            if source == source_name:
                is_muted = False
            r = requests.SetMute(f"{source}cam", is_muted)
            self.ws.call(r)

    def source_loop_of(self, target_index):
        size = len(self.sources)
        if target_index < size:
            return self.sources[target_index]
        else:
            return self.sources[target_index % size]

    def rotate_scene(self):
        has_counter = hasattr(self, "main_counter")
        if has_counter:
            self.main_counter += 1
        else:
            self.main_counter = 0
        view_target = self.source_loop_of(self.main_counter)
        self.setScene("_Main", view_target)
        self.setScene("_Main", view_target, "txt")
        self.setAudioForMain(view_target)
        self.setScene("_Side1", self.source_loop_of(self.main_counter + 1))
        self.setScene("_Side2", self.source_loop_of(self.main_counter + 2))
        log.debug("Main Scene Switch", scene_name=view_target)

    def set_scene_time(self, time_of_day = None):
        # If the event fires at dawn, we want day. If it's at dusk, we want night
        before_dawn = datetime.datetime.now(self.sun_data["tzinfo"]) < self.sun_data["dawn"]
        after_dusk = datetime.datetime.now(self.sun_data["tzinfo"]) >= self.sun_data["dusk"]
        if time_of_day == None:
            if before_dawn or after_dusk:
                time_of_day = "night"
            else:
                time_of_day = "day"

        log.info("Changing scene time", scene_time=time_of_day)
        if time_of_day == "day":
            self.sources = self.day_sources
        elif time_of_day == "night":
            self.sources = self.night_sources
        else:
            self.sources = []

    def set_today_events(self):
        self.sun_data = sun(SEGUIN.observer, date=datetime.date.today(), tzinfo=SEGUIN.timezone)
        self.sun_data["tzinfo"] = SEGUIN.tzinfo

        log.debug(f"Setting today's events", 
            dawn=format_time(self.sun_data["dawn"]), 
            sunrise=format_time(self.sun_data["sunrise"]), 
            sunset=format_time(self.sun_data["sunset"]), 
            dusk=format_time(self.sun_data["dusk"]))