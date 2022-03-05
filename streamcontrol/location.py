from astral import LocationInfo
from astral.sun import sun

SEGUIN = LocationInfo("Seguin", "Texas", "US/Central", 29.563180, -97.894670)


def format_time(dt):
    return dt.strftime("%I:%M %p")


def get_suntime(dt, location=SEGUIN):
    sun_data = sun(location.observer, date=dt, tzinfo=location.timezone)
    sun_data["tzinfo"] = location.tzinfo
    return sun_data
