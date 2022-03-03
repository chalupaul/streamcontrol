import asyncio
from obsmanager import OBSManager
from crons import DailyScheduler        

def main():
    with OBSManager() as obsmgr:
        schedulers = [DailyScheduler()]
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

main()