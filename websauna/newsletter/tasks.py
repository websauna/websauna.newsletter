import logging
import premailer

from websauna.system.core.utils import get_secrets
from websauna.utils.time import now
from websauna.system.task.tasks import ScheduleOnCommitTask, task

from .mailgun import Mailgun
from .interfaces import INewsletterGenerator
from .state import NewsletterState
from .importer import import_all_users


logger = logging.getLogger(__name__)


@task(base=ScheduleOnCommitTask, bind=True)
def send_newsletter_task(self: ScheduleOnCommitTask, subject, preview_email, testmode, now_, import_subscribers):
    """Do user import and newsletter inside a Celery worker process."""

    request = self.request.request  # type: websauna.system.http.Request

    secrets = get_secrets(request.registry)

    if not now_:
        now_ = now()

    if preview_email:
        to = preview_email
        subject = "[PREVIEW] " + subject
    else:
        to = secrets["mailgun.mailing_list"]

    newsletter = request.registry.queryAdapter(request, INewsletterGenerator)

    state = NewsletterState(request)

    text = "Please see the attached HTML mail."

    html = newsletter.render(since=state.get_last_send_timestamp())
    html = premailer.transform(html)

    from_ = secrets["mailgun.from"]
    domain = secrets["mailgun.domain"]
    campaign = now().isoformat()

    mailgun = Mailgun(request.registry)

    if import_subscribers:
        # This may take a looooong time....
        logger.info("Importing subscribers")
        import_all_users(mailgun, request.dbsession, to)

    logger.info("Sending out newsletter %s %s %s %s", subject, to, from_, campaign)
    mailgun.send(domain, to, from_, subject, text, html, campaign)

    if not preview_email:
        # Only mark newsletter send if not prvew
        state.set_last_send_timestamp(now_)