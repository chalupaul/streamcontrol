from dotenv import dotenv_values
from obswebsocket import obsws, requests
import datetime
from astral.sun import sun
from log import LOGGER as log
import constants
from location import SEGUIN, format_time, get_tzinfo
from exceptions import SourceNameNotFound


class OBSWebSocketManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OBSWebSocketManager, cls).__new__(cls)
        return cls.instance
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __init__(self):
        if not self.isConnected():
            self.connect()
    
    def isConnected(self):
        has_ws = hasattr(self, 'ws') and self.ws is not None
        if (has_ws):
            return True
        return False

    def connect(self):
        if self.isConnected():
            return
        config = dotenv_values()
        obs_host = config.get("obs_host", "localhost")
        obs_port = config.get("obs_port", 4444)
        obs_password = config.get("obs_password", "secret")
        self.ws = obsws(obs_host, obs_port, obs_password)
        self.ws.connect()
    
    def disconnect(self):
        if self.isConnected():
            self.ws.disconnect()

class OBSManager(OBSWebSocketManager):  
    def __init__(self):
        super().__init__()
        if not hasattr(self, "sun_data"):
            self.set_today_events()

    def set_scene(self, scene_name, source_name, source_type="cam"):
        sources = self.get_sources()
        if source_name not in sources:
            raise SourceNameNotFound
        for source in sources:
            is_target = False
            if source == source_name:
                is_target = True
            r = requests.SetSceneItemRender(f"_{source}{source_type}", is_target, scene_name=scene_name)
            self.ws.call(r)
    
    def set_audio_for_main(self, source_name):
        sources = self.get_sources()
        if source_name not in sources:
            raise SourceNameNotFound
        for source in sources:
            is_muted = True
            if source == source_name:
                is_muted = False
            r = requests.SetMute(f"{source}cam", is_muted)
            self.ws.call(r)

    def source_loop_of(self, counter):
        sources = self.get_sources()
        size = len(sources)
        if counter < size:
            return sources[counter]
        else:
            return sources[counter % size]

    def rotate_scene(self):
        has_counter = hasattr(self, "main_counter")
        if has_counter:
            self.main_counter += 1
        else:
            self.main_counter = 0
        view_target = self.source_loop_of(self.main_counter)
        #self.set_scene("_Main", view_target)
        #self.set_scene("_Main", view_target, "txt")
        #self.set_audio_for_main(view_target)
        #self.set_scene("_Side1", self.source_loop_of(self.main_counter + 1))
        #self.set_scene("_Side2", self.source_loop_of(self.main_counter + 2))
        time_of_day = "night" if self.is_night() else "day"
        log.debug("Main Scene Switch", scene_name=view_target, sources=time_of_day)

    def is_night(self):
        # If the event fires at dawn, we want day. If it's at dusk, we want night
        before_dawn = datetime.datetime.now(self.sun_data["tzinfo"]) < self.sun_data["dawn"]
        after_dusk = datetime.datetime.now(self.sun_data["tzinfo"]) >= self.sun_data["dusk"]
        if before_dawn or after_dusk:
            return True
        return False

    def get_sources(self):
        if self.is_night():
            sources = constants.NIGHT_SOURCES
        else:
            sources = constants.DAY_SOURCES
        return sources

    def set_today_events(self):
        self.sun_data = sun(SEGUIN.observer, date=datetime.date.today(), tzinfo=SEGUIN.timezone)
        self.sun_data["tzinfo"] = SEGUIN.tzinfo

        log.info(f"Setting today's events", 
            dawn=format_time(self.sun_data["dawn"]), 
            sunrise=format_time(self.sun_data["sunrise"]), 
            sunset=format_time(self.sun_data["sunset"]), 
            dusk=format_time(self.sun_data["dusk"]))