from __future__ import annotations

import datetime


def get_current_date_time() -> str:
    """Return the current date and time in UTC format."""
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
