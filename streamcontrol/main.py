import asyncio
from streamcontrol import schedulers
from streamcontrol.log import LOGGER as log

def get_schedulers():
    """Finds a bunch of scheduler classes within the schedulers module"""
    base_class = getattr(schedulers, "BaseScheduler")
    found_schedulers = []
    members = [s for s in dir(schedulers) if not s.startswith("_")]
    for member in members:
        member_class = getattr(schedulers, member)
        has_base_class = hasattr(member_class, "__bases__")
        if has_base_class and base_class in member_class.__bases__:
            found_schedulers.append(member_class)
    return found_schedulers

def main():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop_policy().get_event_loop()
    found_schedulers = get_schedulers()
    for s in found_schedulers:
        s()
    log.debug("Schedulers loaded", schedulers=found_schedulers)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()