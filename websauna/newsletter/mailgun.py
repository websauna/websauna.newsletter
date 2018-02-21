"""Mailgun based newsletter management."""
# Standard Library
import logging

# Pyramid
from pyramid.registry import Registry

import requests

# Websauna
from websauna.system.core.utils import get_secrets


logger = logging.getLogger(__name__)


def yesify(val):
    """Because booleans where not invented 150 years ago."""
    return "yes" if val else "no"


class MailgunError(Exception):
    """Mailgun API did not like a particular request."""


class Mailgun:
    """Simple mailgun mailing list API wrapper for Websauna."""

    def __init__(self, registry: Registry, api_url=None, timeout=10):
        secrets = get_secrets(registry)
        self.api_key = secrets["mailgun.api_key"]
        if api_url:
            self.api_url = api_url
        else:
            self.api_url = "https://api.mailgun.net/v3"

        # Open HTTP 1.1 Keep-Alive session
        self.session = requests.Session()
        self.timeout = timeout

    def make_request(self, func: str, method="POST", **data) -> dict:
        """Call Mailgun API.

        :return: Response parsed JSON dict
        """

        url = self.api_url + "/" + func

        resp = self.session.request(
            method,
            url,
            auth=('api', self.api_key),
            data=data,
            timeout=self.timeout)

        if resp.status_code != 200:
            raise MailgunError("Mailgun returned non-200 code for URL {} {}: {} {}".format(method, url, resp.status_code, resp.text))

        return resp.json()

    def create_list(self, address: str, description: str) -> dict:
        """Create a new mailign list"""
        return self.make_request("lists", address=address, description=description)

    def delete_list(self, address: str) -> dict:
        """Delete a new mailign list"""
        return self.make_request("lists/{}".format(address), method="DELETE")

    def list_members(self, address: str) -> dict:
        """Get mailing list members pagination object"""
        return self.make_request("lists/{}/members/pages".format(address), method="GET")

    def update_subscription(self, address: str, data: dict) -> dict:
        """Update subscription information

        http://mailgun-documentation.readthedocs.io/en/latest/api-mailinglists.html#mailing-lists

        :param address: Mailing list
        :param data: dict like {"address": user.email, "name": user.friendly_name, "upsert": upsert and "yes" or "no",}
        """
        return self.make_request("lists/{}/members".format(address), **data)

    def send(self, domain: str, to: str, from_: str, subject: str, text: str, html: str, campaign=None, testmode=False, tracking=True, tracking_clicks=True, tracking_opens=True):
        """Send a newsletter or single message.

        See

        * https://documentation.mailgun.com/user_manual.html#mailing-lists

        * https://documentation.mailgun.com/api-sending.html#sending
        """

        data = {
            "to": to,
            "from": from_,
            "text": text,
            "html": html,
            "subject": subject,
            "testmode": yesify(testmode),
            "o:tracking": yesify(tracking),
            "o:tracking-clicks": yesify(tracking_clicks),
            "o:tracking-opens": yesify(tracking_opens),
        }

        if campaign:
            data["o:campaign"] = yesify(campaign)

        return self.make_request("{}/messages".format(domain), **data)
