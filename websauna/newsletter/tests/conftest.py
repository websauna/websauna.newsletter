# Pyramid
import transaction

import pytest

# Websauna
from websauna.newsletter.importer import import_all_users
from websauna.newsletter.mailgun import Mailgun
from websauna.system.core.utils import get_secrets
from websauna.tests.utils import create_user


@pytest.fixture
def mailgun(registry):
    m = Mailgun(registry)
    return m


@pytest.fixture()
def mailing_list(mailgun, registry):
    secrets = get_secrets(registry)
    list_address = secrets["mailgun.mailing_list"]

    try:
        mailgun.delete_list(list_address)
    except Exception:
        # Clean up previous test run if interrupted
        pass

    mailgun.create_list(list_address, "Unit test list")
    return list_address


@pytest.fixture()
def domain(mailgun, registry):
    """Outbound domain"""
    secrets = get_secrets(registry)
    return secrets["mailgun.domain"]


@pytest.fixture()
def populated_mailing_list(mailgun, dbsession, registry, mailing_list):
    with transaction.manager:
        create_user(dbsession, registry)

    count = import_all_users(mailgun, dbsession, mailing_list)
    assert count == 1
    return mailing_list
