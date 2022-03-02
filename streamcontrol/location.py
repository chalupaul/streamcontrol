from astral import LocationInfo
import pytz

SEGUIN = LocationInfo("Seguin", "Texas", "US/Central", 29.563180, -97.894670)

def format_time(dt):
    return dt.strftime("%I:%M %p")

def get_tzinfo(tzinfo):
    return pytz.timezone(tzinfo)