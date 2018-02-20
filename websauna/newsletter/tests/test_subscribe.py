"""Subscription tests."""

# Websauna
from websauna.newsletter.views import subscribe_email


def test_subscribe_email(mailgun, mailing_list, test_request):
    """Subscribe an email address without a user."""

    subscribe_email(test_request, "example@example.com")

    paginator = mailgun.list_members(mailing_list)
    items = paginator["items"]
    assert len(items) == 1
    assert items[0]["address"] == "example@example.com"
