from datetime import datetime, timezone

def to_naive_utc(dt:datetime) -> datetime:
    return dt.astimezone(timezone.utc).replace(tzinfo=None)