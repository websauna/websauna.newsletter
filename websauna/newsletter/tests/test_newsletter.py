"""Mailgun API integration tests."""
# Standard Library
import datetime

# Pyramid
import transaction

# Websauna
from websauna.newsletter.sender import send_newsletter
from websauna.newsletter.state import NewsletterState
from websauna.system.core.redis import get_redis


def test_send_preview(mailgun, populated_mailing_list, domain, test_request):
    """Send out a news letter preview."""

    # Make sure we run on empty state
    redis = get_redis(test_request)
    redis.delete(NewsletterState.REDIS_NEWSLETTER_TIMESTAMP)

    now = datetime.datetime(1980, 1, 15)

    with transaction.manager:
        # This is triggered only on commit
        send_newsletter(test_request, "Test subject", testmode=True, now_=now)

    state = NewsletterState(test_request)

    assert state.get_last_send_timestamp().year == 1980
