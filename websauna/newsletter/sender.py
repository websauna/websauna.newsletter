# Standard Library
import logging

from .tasks import send_newsletter_task


logger = logging.getLogger(__name__)


def send_newsletter(request, subject: str, preview_email=None, testmode=False, now_=None, import_subscribers=False):
    """Send newsletter.

    The HTML is mangled through premailer.

    Performs the operation asynchronously in a Celery task. The task dispatch is triggered only on commit.

    :param preview_email: Fill in to send a preview
    :param testmode: As in Mailgun parameters
    :param now_: Override timestamp to newsletter state
    :param import_subscribers: Import Websauna userbase as subscribers for the newsletter
    """

    logger.info("Scheduling newsletter task %s, preview %s, import subscribers %s", subject, preview_email, import_subscribers)
    send_newsletter_task.apply_async(args=(subject, preview_email, testmode, now_, import_subscribers), tm=request.tm)
