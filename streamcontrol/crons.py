import aiocron
import asyncio
import datetime
from obsmanager import OBSManager

class BaseScheduler(object):  
    @staticmethod 
    async def wait_until(dt, tz=datetime.timezone.utc):
        now = datetime.datetime.now(tz)
        await asyncio.sleep((dt - now).total_seconds())

    @staticmethod
    async def run_at(coro, dt, tz=datetime.timezone.utc):
        await BaseScheduler.wait_until(dt, tz)
        return await coro()

class DailyScheduler(BaseScheduler):
    def __init__(self):
        obsmgr = OBSManager()
        self.obsmgr = obsmgr
        loop = asyncio.get_event_loop()
            
        @aiocron.crontab("*/2 * * * *")
        async def scene_rotation():
            obsmgr.rotate_scene()
        
        @aiocron.crontab("1 3 * * *")
        async def set_today_events():
            @asyncio.coroutine
            def set_day_scenes():
                obsmgr.set_scene_time("day")            

            @asyncio.coroutine
            def set_night_scenes():
                obsmgr.set_scene_time("night")

            obsmgr.set_today_events()
            tzinfo = obsmgr.sun_data["tzinfo"]
            dawn = obsmgr.sun_data["dawn"]
            dusk = obsmgr.sun_data["dusk"]

            loop.create_task(self.run_at(set_day_scenes, dawn, tzinfo))
            loop.create_task(self.run_at(set_night_scenes, dusk, tzinfo))


