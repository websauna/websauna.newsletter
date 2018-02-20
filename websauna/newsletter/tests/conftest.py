# Pyramid
import transaction

import json
import requests

import pytest

# Websauna
from websauna.newsletter.importer import import_all_users
from websauna.newsletter.mailgun import Mailgun
from websauna.system.core.utils import get_secrets
from websauna.tests.utils import create_user

MAILGUN_RESPONSES = {
    'https://api.mailgun.net/v3/lists/foobar@not-exist.com': {
        'DELETE': {
            'status_code': 404,
            'body': {
                'message': 'Mailing list does not exist',
                'address': 'unit-testing@mailgun.websauna.org'
            }
        }
    },
    'https://api.mailgun.net/v3/lists/unit-testing@mailgun.websauna.org': {
        'DELETE': {
            'status_code': 200,
            'body': {
                'message': 'Mailing list has been deleted',
                'address': 'unit-testing@mailgun.websauna.org'
            }
        }
    },
    'https://api.mailgun.net/v3/mailgun.websauna.org/messages': {
        'POST': {
            'status_code': 200,
            'body': {
                'message': 'Queued. Thank you.',
                'id': '<20111114174239.25659.5817@samples.mailgun.org>'
            }
        }
    },
    'https://api.mailgun.net/v3/lists/unit-testing@mailgun.websauna.org/members': {
        'POST': {
            'status_code': 200,
            'body': {
                'member': {
                    'name': 'example@example.com',
                    'subscribed': True,
                    'address': 'example@example.com'
                },
                'message': 'Mailing list member has been created'
            }
        }
    },
    'https://api.mailgun.net/v3/lists/unit-testing@mailgun.websauna.org/members/pages': {
        'GET': {
            'status_code': 200,
            'body': {
                'items': [
                    {
                        'name': 'example@example.com',
                        'subscribed': True,
                        'address': 'example@example.com'
                    }
                ],
                'paging': {
                    'first': 'https://url_to_first_page',
                    'last': 'https://url_to_last_page',
                    'next': 'http://url_to_next_page',
                    'previous': 'http://url_to_previous_page'
                }
            }
        }
    },
    'https://api.mailgun.net/v3/lists': {
        'POST': {
            'status_code': 200,
            'body': {
                'message': 'Mailing list has been created',
                'list': {
                    'created_at': 'Tue, 06 Mar 2012 05:44:45 GMT',
                    'address': 'unit-testing@mailgun.websauna.org',
                    'members_count': 0,
                    'description': 'Websauna developers list',
                    'name': ''
                }
            }
        }
    },
}


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

    import_all_users(mailgun, dbsession, mailing_list)
    return mailing_list


@pytest.fixture(scope='session')
def mock_request():
    def mock_requests_response(self, method, url, *args, **kwargs):
        """Mock a response"""
        headers = {'content-type': 'application/json'}
        data = MAILGUN_RESPONSES[url][method]
        body = data['body']
        status_code = data['status_code']
        resp = requests.Response()
        resp.status_code = status_code
        resp.headers = headers
        resp._content = json.dumps(body).encode('utf8')
        return resp
    return mock_requests_response


@pytest.fixture(autouse=True)
def mock_api(monkeypatch, mock_request):
    """Mock all api calls."""
    monkeypatch.setattr(requests.sessions.Session, 'request', mock_request)
