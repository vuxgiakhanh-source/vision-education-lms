from datetime import datetime, timedelta, timezone


def center_local_now() -> datetime:
    """Return the center's Vietnam wall time without a UTC offset."""
    return datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
