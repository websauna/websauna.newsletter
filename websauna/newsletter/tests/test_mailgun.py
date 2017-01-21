"""Mailgun API integration tests."""
import pytest
import transaction

from websauna.newsletter.mailgun import Mailgun, MailgunError
from websauna.newsletter.importer import import_all_users
from websauna.system.core.utils import get_secrets
from websauna.tests.utils import create_user


@pytest.fixture
def mailgun(registry):
    m = Mailgun(registry)
    return m


@pytest.fixture()
def mailing_list(mailgun, registry):
    secrets = get_secrets(registry)
    list_address = secrets["mailgun.mailing-list"]

    try:
        mailgun.delete_list(list_address)
    except:
        # Clean up previous test run if interrupted
        pass

    mailgun.create_list(list_address, "Unit test list")
    return list_address

@pytest.fixture()
def domain(mailgun, registry):
    """Outbound domain"""
    secrets = get_secrets(registry)
    return secrets["domain"]


@pytest.fixture()
def populated_mailing_list(mailgun, dbsession, registry, mailing_list):
    with transaction.manager:
        create_user(dbsession, registry)

    count = import_all_users(mailgun, dbsession, mailing_list)
    assert count == 1
    return mailing_list


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



