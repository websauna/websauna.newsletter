import datetime

from websauna.system.http import Request


class NewsletterState:
    """Newsletter state management."""

    #: Redis key when the last news letter was send
    REDIS_NEWSLETTER_TIMESTAMP = "newsletter_sent_timestamp"

    def __init__(self, request: Request):
        self.request = request

    def send(self, preview: bool):
        pass

    def get_last_send_timestamp(self) -> datetime.datetime:
        """Get UNIX timestamp when the last newsletter went out."""
        return None

    def save_newsletter(self, emails, campaign_id, renderer_html):
        """Store newsletter data for later usage.."""