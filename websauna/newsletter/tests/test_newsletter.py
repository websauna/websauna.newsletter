"""Mailgun API integration tests."""

from websauna.newsletter.sender import send_newsletter


def test_send_preview(mailgun, populated_mailing_list, domain, test_request):
    """Send out a news letter preview."""
    send_newsletter(test_request, "Test subject", testmode=True)



