from faulthandler import disable
import aiocron
import asyncio
import datetime
from streamcontrol.obsmanager import OBSManager
from streamcontrol.location import SEGUIN
from streamcontrol.templates import Templates
from streamcontrol.location import format_time
from types import FunctionType
from streamcontrol.log import LOGGER as log

class BaseScheduler(object):  
    def __init__(self):
        self.obsmgr = OBSManager()
        self._schedule()

    @staticmethod 
    async def wait_until(dt, tz=SEGUIN.timezone):
        """Sleep for a total seconds between now and dt (datetime)"""
        now = datetime.datetime.now(tz)
        await asyncio.sleep((dt - now).total_seconds())

    @staticmethod
    async def run_at(coro, dt, tz=SEGUIN.timezone):
        """Schedule a job for a particular time via sleeping"""
        await BaseScheduler.wait_until(dt, tz)
        return await coro()
    
    def _schedule(self): 
        """Reflects and executes a list of crons as class methods.

        aiocrons themselves should be defined as inner functions
        Executing the method will register them.
        """

        functions = type(self).__dict__.items()
        for func_name, func_ptr in functions:
            is_function = type(func_ptr) == FunctionType
            private = func_name.startswith('_')
            if is_function and not private:
                log.debug("Registering cron", cron_name = func_name)
                func_ptr(self)

class SceneRotationScheduler(BaseScheduler):

    def two_minute_rotator(self):    
        """Rotate the obs scene every 2 minutes"""
        @aiocron.crontab("*/2 * * * *")
        async def scene_rotation():
            self.obsmgr.rotate_scene()
    
    def update_solar_times(self):
        """Update dawn/dusk time for current day"""
        @aiocron.crontab("1 3 * * *")
        async def solar_times():
            self.obsmgr.set_today_events()
        
        
class MorningChoreStreamScheduler(BaseScheduler):
    def sunrise_chores(self):
        """Sunrise chore stream. Schedule after solar_times()"""
        @aiocron.crontab("* * * * 1-5")
        async def morning_chore_stream():
            template = Templates.next_event
            event_time = format_time(self.obsmgr.sun_data["dawn"])
            event_agenda = "Morning Chore Livestream"
            template.render_to_file("morning_chores.txt", agenda=event_agenda, time=event_time)
            log.debug("Updating event time", agenda=event_agenda, time=event_time)