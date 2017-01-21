from websauna.system.core.utils import get_secrets
from websauna.utils.time import now

from .mailgun import Mailgun
from .interfaces import INewsletterGenerator


def send_newsletter(request, subject: str, preview_email=None):
    """Send newsletter.

    :param request:
    :param preview_email: Fill in to send a preview
    :return:
    """
    secrets = get_secrets(request.registry)

    if preview_email:
        to = preview_email
    else:
        to = secrets["mailgun.mailing-list"]

    newsletter = request.registry.queryAdapter(request, INewsletterGenerator)

    text = "Please see the attached HTML mail."
    html = newsletter.render()
    from_ = secrets["mailgun.from"]
    domain = secrets["mailgun.domain"]
    api_key = secrets["mailgun.api_key"]
    campaign = now().isoformat()

    mailgun = Mailgun(request.registry)
    mailgun.send(domain, to, from_, subject, text, html, campaign)