# Standard Library
import datetime

# Websauna
from websauna.system.core.redis import get_redis
from websauna.system.http import Request


class NewsletterState:
    """Newsletter state management.

    State is stord within redis.
    """

    #: Redis key when the last news letter was send
    REDIS_NEWSLETTER_TIMESTAMP = "newsletter_sent_timestamp"

    def __init__(self, request: Request):
        self.request = request
        self.redis = get_redis(self.request)

    def set_last_send_timestamp(self, now: datetime.datetime):
        ts = now.timestamp()
        self.redis.set(self.REDIS_NEWSLETTER_TIMESTAMP, ts)

    def get_last_send_timestamp(self) -> datetime.datetime:
        """Get UNIX timestamp when the last newsletter went out."""
        val = self.redis.get(self.REDIS_NEWSLETTER_TIMESTAMP)
        if not val:
            return None

        dt = datetime.datetime.utcfromtimestamp(float(val)).replace(tzinfo=datetime.timezone.utc)
        return dt
