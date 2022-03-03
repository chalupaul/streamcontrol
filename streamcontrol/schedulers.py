import aiocron
import asyncio
import datetime
from obsmanager import OBSManager
from types import FunctionType
from log import LOGGER as log

class BaseScheduler(object):  
    def __init__(self):
        self._schedule()

    @staticmethod 
    async def wait_until(dt, tz=datetime.timezone.utc):
        """Sleep for a total seconds between now and dt (datetime)"""
        now = datetime.datetime.now(tz)
        await asyncio.sleep((dt - now).total_seconds())

    @staticmethod
    async def run_at(coro, dt, tz=datetime.timezone.utc):
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

class DailyScheduler(BaseScheduler):
    def __init__(self):
        super().__init__()
        self.obsmgr = OBSManager()


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
        
        

