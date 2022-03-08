import datetime

from obswebsocket import obsws, requests

from streamcontrol import constants
from streamcontrol.config import config
from streamcontrol.exceptions import SourceNameNotFound
from streamcontrol.location import format_time, get_suntime
from streamcontrol.log import LOGGER as log


class OBSWebSocketManager(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
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
        has_ws = hasattr(self, "ws") and self.ws is not None
        if has_ws:
            return True
        return False

    def connect(self):
        if self.isConnected():
            return
        self.ws = obsws(config.obs_host, config.obs_port, config.obs_password)
        self.ws.connect()

    def disconnect(self):
        if self.isConnected():
            self.ws.disconnect()


class OBSManager(OBSWebSocketManager):
    def __init__(self):
        super().__init__()
        if not hasattr(self, "sun_data"):
            self.set_today_events()

    def set_scene(
        self, scene_name, source_name, source_type="cam", disable_source=False
    ):
        sources = self.get_sources(all=True)
        if source_name not in sources:
            raise SourceNameNotFound
        for source in sources:
            is_target = False
            if source == source_name and not disable_source:
                is_target = True
            if not source.startswith("_"):
                source = f"_{source}"
            r = requests.SetSceneItemRender(
                f"{source}{source_type}", is_target, scene_name=scene_name
            )
            self.ws.call(r)

    def enable_source_for_scene(self, scene_name, source_name):
        self.set_scene(scene_name, source_name, source_type="")

    def disable_source_for_scene(self, scene_name, source_name):
        self.set_scene(scene_name, source_name, source_type="", disable_source=True)

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
        self.set_scene("_Main", view_target)
        self.set_scene("_Main", view_target, "txt")
        self.set_audio_for_main(view_target)
        self.set_scene("_Side1", self.source_loop_of(self.main_counter + 1))
        self.set_scene("_Side2", self.source_loop_of(self.main_counter + 2))
        time_of_day = "night" if self.is_night() else "day"
        log.debug("Main Scene Switch", scene_name=view_target, sources=time_of_day)

    def is_night(self):
        # If the event fires at dawn, we want day. If it's at dusk, we want night
        before_dawn = (
            datetime.datetime.now(self.sun_data["tzinfo"]) < self.sun_data["dawn"]
        )
        after_dusk = (
            datetime.datetime.now(self.sun_data["tzinfo"]) >= self.sun_data["dusk"]
        )
        if before_dawn or after_dusk:
            return True
        return False

    def get_sources(self, all=False):
        if all:
            sources = list(set(constants.NIGHT_SOURCES + constants.DAY_SOURCES))
        else:
            if self.is_night():
                sources = constants.NIGHT_SOURCES
            else:
                sources = constants.DAY_SOURCES
        return sources

    def set_today_events(self):
        self.sun_data = get_suntime(datetime.date.today())

        log.info(
            "Setting today's events",
            dawn=format_time(self.sun_data["dawn"]),
            sunrise=format_time(self.sun_data["sunrise"]),
            sunset=format_time(self.sun_data["sunset"]),
            dusk=format_time(self.sun_data["dusk"]),
        )
