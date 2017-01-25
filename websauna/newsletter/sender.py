from websauna.system.core.utils import get_secrets
from websauna.utils.time import now

from .mailgun import Mailgun
from .interfaces import INewsletterGenerator
from .state import NewsletterState
from .importer import import_all_users


def send_newsletter(request, subject: str, preview_email=None, testmode=False, now_=None, import_subscribers=False):
    """Send newsletter.

    :param request:
    :param preview_email: Fill in to send a preview
    :return:
    """
    secrets = get_secrets(request.registry)

    if not now_:
        now_ = now()

    if preview_email:
        to = preview_email
    else:
        to = secrets["mailgun.mailing_list"]

    newsletter = request.registry.queryAdapter(request, INewsletterGenerator)

    state = NewsletterState(request)

    text = "Please see the attached HTML mail."
    html = newsletter.render(since=state.get_last_send_timestamp())
    from_ = secrets["mailgun.from"]
    domain = secrets["mailgun.domain"]
    campaign = now().isoformat()

    mailgun = Mailgun(request.registry)

    if import_subscribers:
        import_all_users(mailgun, request.dbsession, to)

    mailgun.send(domain, to, from_, subject, text, html, campaign)

    state.set_last_send_timestamp(now_)