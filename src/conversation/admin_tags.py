from bot.lib.snowflake import snowflake2utc
from datetime import datetime

def admin_tag_status_datetime(statusid: int):
    """Return ISO datetime string from status id
    """
    ts = snowflake2utc(statusid)
    return datetime.utcfromtimestamp(ts).isoformat()