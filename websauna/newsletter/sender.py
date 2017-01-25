from .tasks import send_newsletter_task


def send_newsletter(request, subject: str, preview_email=None, testmode=False, now_=None, import_subscribers=False):
    """Send newsletter.

    The HTML is mangled through premailer.

    Performs the operation asynchronously in a Celery task. The task dispatch is triggered only on commit.

    :param preview_email: Fill in to send a preview
    :param testmode: As in Mailgun parameters
    :param now_: Override timestamp to newsletter state
    :param import_subscribers: Import Websauna userbase as subscribers for the newsletter
    """

    send_newsletter_task.apply_async(args=(subject, preview_email, testmode, now_, import_subscribers), tm=request.transaction_manager)