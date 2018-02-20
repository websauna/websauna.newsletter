# Standard Library
from datetime import datetime
from typing import Tuple

# Pyramid
from zope.interface import Interface


class INewsletterGenerator(Interface):
    """Newsletter interface.

    Allow to configure different newsletters for a website.

    Registered as a adapter for request.
    """

    def render(since: datetime) -> Tuple[str, str]:
        """Render the current newsletter payload.

        :param since: When the last newsletter was sent or None if the first outgoing newsletter on this site.

        :return: tuple (subject, html)
        """
