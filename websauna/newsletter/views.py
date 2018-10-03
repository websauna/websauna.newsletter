# Pyramid
import colander
import deform
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound

# Websauna
from websauna.system.core import messages
from websauna.system.core.route import simple_route
from websauna.system.core.sitemap import include_in_sitemap
from websauna.system.core.utils import get_secrets
from websauna.system.form.schema import CSRFSchema
from websauna.system.http import Request

from .mailgun import Mailgun


class NewsletterSubscriptionSchema(CSRFSchema):
    """Newsletter subscription schema."""

    email = colander.Schema(colander.String(), validator=colander.Email())
    came_from = colander.Schema(colander.String(), validator=colander.url)


def subscribe_email(request: Request, email: str):
    """Subscribe an email address to our default mailing list.

    Don't change existing subscription status.
    Save form data from appstruct
    """
    mailgun = Mailgun(request.registry)
    secrets = get_secrets(request.registry)
    address = secrets["mailgun.mailing_list"]

    return mailgun.update_subscription(address, {
        "address": email,
        "email": email,
        "upsert": "yes"
    })


@simple_route("/subscribe-newsletter", route_name="subscribe_newsletter")
@include_in_sitemap(False)
def subscribe_newsletter(request: Request):
    """Newsletter Subscription view."""
    schema = NewsletterSubscriptionSchema().bind(request=request)
    form = deform.Form(schema)

    # In case of validation error, we return the user to the form
    came_from = request.referer or request.route_url('home')

    if request.method != "POST":
        return HTTPBadRequest("POST-only endpoint")

    # User submitted this form
    if 'subscribe' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
            email = appstruct["email"]
            came_from = appstruct["came_from"]
            subscribe_email(request, email)
            # Thank user and take them to the next page
            msg = "<strong>{email}</strong> has been subscribed to the newsletter.".format(email=email)
            msg_class = 'info'
        except deform.ValidationFailure as e:
            # Render a form version where errors are visible next to the fields,
            # and the submitted values are posted back
            msg = "Email was not valid."
            msg_class = 'error'

        messages.add(request, kind=msg_class, msg=msg)
        return HTTPFound(came_from)
    else:
        # We don't know which control caused form submission
        return HTTPBadRequest("Unknown form button pressed")
