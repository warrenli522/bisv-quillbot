from datetime import datetime, time
from zoneinfo import ZoneInfo

def parse_date(s: str, tz: str = "America/Los_Angeles") -> datetime:
    """
    Parses a date string in MM-DD-YY or MM-DD-YY-HH-MM format and returns
    a timezone-aware datetime object. If the time is not provided, defaults
    to 11:59:59 PM. If 'now' is provided, returns the current datetime.
    
    :param s: Date string to parse
    :type s: str
    :param tz: Timezone name
    :type tz: str
    :return: Parsed datetime object
    :rtype: datetime
    """
    s = s.strip().lower()
    if s == "now":
        return datetime.now(ZoneInfo(tz))
    formats_with_time = "%m-%d-%y-%H-%M"
    formats_date_only = ["%m-%d-%y", "%m-%d-%Y"]

    try:
        dt = datetime.strptime(s, formats_with_time)
    except ValueError:
        dt_date = None
        for fmt in formats_date_only:
            try:
                dt_date = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        if dt_date is None:
            raise
        dt = datetime.combine(dt_date.date(), time(23, 59, 59))

    return dt.replace(tzinfo=ZoneInfo(tz))
