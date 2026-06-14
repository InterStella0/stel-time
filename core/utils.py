import datetime
import functools
import re
from zoneinfo import available_timezones, ZoneInfo


@functools.cache
def get_timezones() -> list[str]:
    timezones = available_timezones()
    return list(timezones)


_OFFSET_RE = re.compile(r'^([+-])(\d{1,2})(?::(\d{2}))?$')

def parse_utc_offset(text: str) -> datetime.timedelta | None:
    """Parse strings like +1, -5, +5:30 into a timedelta offset."""
    m = _OFFSET_RE.match(text.strip())
    if not m:
        return None
    sign = 1 if m.group(1) == '+' else -1
    hours = int(m.group(2))
    minutes = int(m.group(3) or 0)
    return datetime.timedelta(hours=sign * hours, minutes=sign * minutes)


@functools.cache
def get_timezones_by_offset(offset_td: datetime.timedelta) -> list[str]:
    """Return all timezone names whose current UTC offset matches offset_td."""
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    result = []
    for name in available_timezones():
        tz_offset = now.astimezone(ZoneInfo(name)).utcoffset()
        if tz_offset == offset_td:
            result.append(name)
    return result
