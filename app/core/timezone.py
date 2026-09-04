"""
Timezone Utility for Indian Standard Time (IST, UTC+05:30)
Standardizes all datetime operations and timestamp generations across the application.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))


def get_current_time() -> datetime:
    """
    Returns the current datetime localized to Indian Standard Time (IST, UTC+05:30).
    """
    return datetime.now(IST)


def get_current_iso() -> str:
    """
    Returns the current IST timestamp formatted as an ISO 8601 string.
    """
    return get_current_time().isoformat()


def get_current_year() -> int:
    """
    Returns the current calendar year in IST.
    """
    return get_current_time().year


def to_aware_ist(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensures a datetime object loaded from database is timezone-aware in IST.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST)
    return dt.astimezone(IST)


def time_diff_seconds(dt1: datetime, dt2: datetime) -> float:
    """
    Safely computes total seconds difference (dt1 - dt2) regardless of offset-naive/aware status.
    """
    a = to_aware_ist(dt1)
    b = to_aware_ist(dt2)
    if a is None or b is None:
        return 0.0
    return (a - b).total_seconds()
