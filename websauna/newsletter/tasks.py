# Standard Library
import logging

import premailer

# Websauna
from websauna.system.core.utils import get_secrets
from websauna.system.model.retry import retryable
from websauna.system.task.tasks import ScheduleOnCommitTask
from websauna.system.task.tasks import task
from websauna.utils.time import now

from .importer import import_all_users
from .interfaces import INewsletterGenerator
from .mailgun import Mailgun
from .state import NewsletterState


logger = logging.getLogger(__name__)


@task(base=ScheduleOnCommitTask, bind=True)
def send_newsletter_task(self: ScheduleOnCommitTask, subject, preview_email, testmode, now_, import_subscribers):
    """Do user import and newsletter inside a Celery worker process.

    We carefully split transaction handling to several parts.
    """

    # from celery.contrib import rdb ; rdb.set_trace()

    request = self.get_request()

    secrets = get_secrets(request.registry)

    if not now_:
        now_ = now()

    mailing_list = secrets["mailgun.mailing_list"]

    if preview_email:
        to = preview_email
        subject = "[PREVIEW] " + subject
    else:
        to = mailing_list

    newsletter = request.registry.queryAdapter(request, INewsletterGenerator)

    state = NewsletterState(request)

    text = "Please see the attached HTML mail."

    @retryable(tm=request.tm)
    def render_tx():
        """Run HTML rendering in its own transaction, as it most likely reads database."""
        return newsletter.render(since=state.get_last_send_timestamp())

    html = render_tx()
    html = premailer.transform(html)

    from_ = secrets["mailgun.from"]
    domain = secrets["mailgun.domain"]
    campaign = now().isoformat()

    mailgun = Mailgun(request.registry)

    if import_subscribers:
        # This may take a looooong time....
        logger.info("Importing subscribers")
        import_all_users(mailgun, request.dbsession, mailing_list, tm=request.tm)

    logger.info("Sending out newsletter %s %s %s %s %s", domain, subject, to, from_, campaign)
    mailgun.send(domain, to, from_, subject, text, html, campaign)

    if not preview_email:
        # Only mark newsletter send if not preview
        state.set_last_send_timestamp(now_)
