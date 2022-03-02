import asyncio
from obsmanager import OBSManager
from crons import DailyScheduler        

def main():
    with OBSManager() as obsmgr:
        schedulers = [DailyScheduler()]
        loop = asyncio.get_event_loop()  
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

main()