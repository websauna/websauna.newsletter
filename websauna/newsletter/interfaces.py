from typing import Tuple

from zope.interface import Interface


class INewsletterGenerator(Interface):
    """Newsletter interface.

    Allow to configure different newsletters for a website.

    Registered as a adapter for request.
    """

    def render() -> [str, str]:
        """Render the current newsletter payload.

        :return: tuple (subject, html)
        """

