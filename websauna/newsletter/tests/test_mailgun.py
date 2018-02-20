"""Mailgun API integration tests."""
import pytest

# Websauna
from websauna.newsletter.mailgun import MailgunError


def test_api_error(dbsession, registry, mailgun):
    """We get exception on API error."""

    with pytest.raises(MailgunError):
        mailgun.delete_list("foobar@not-exist.com")


def test_import_subscribers(dbsession, registry, mailgun, populated_mailing_list):
    """Import Websauna users to Mailgun list."""
    paginator = mailgun.list_members(populated_mailing_list)
    items = paginator["items"]
    assert len(items) == 1
    assert items[0]["address"] == "example@example.com"


def test_send_news_letter(mailgun, populated_mailing_list, domain):
    """Send out a news letter."""

    text = """Please see HTML mail"""
    html = """<a href="%mailing_list_unsubscribe_url%">Unsubscribe</a>"""
    to = populated_mailing_list
    from_ = "example@" + domain
    subject = "Test message"
    domain = domain
    campaign = "TAGGGGED"
    testmode = True

    resp = mailgun.send(domain, to, from_, subject, text, html, campaign, testmode)
    assert "id" in resp
