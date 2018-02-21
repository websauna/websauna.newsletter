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
    email = colander.Schema(colander.String(), validator=colander.Email())


def subscribe_email(request: Request, email: str):
    """Subscribe an email address to our default mailing list.

    Don't change existing subscription status.
    """
    # Save form data from appstruct
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

    schema = NewsletterSubscriptionSchema().bind(request=request)
    form = deform.Form(schema)

    # User submitted this form
    if request.method == "POST":
        if 'subscribe' in request.POST:
            try:
                appstruct = form.validate(request.POST.items())
                email = appstruct["email"]

                subscribe_email(request, email)

                # Thank user and take him/her to the next page
                messages.add(request, kind="info", html=True, msg="<strong>{}</strong> has been subscribed to the newsletter.".format(email))
                return HTTPFound(request.route_url("home"))

            except deform.ValidationFailure as e:
                # Render a form version where errors are visible next to the fields,
                # and the submitted values are posted back
                messages.add(request, kind="error", msg="Email was not valid")
                return HTTPFound(request.route_url("home"))
        else:
            # We don't know which control caused form submission
            return HTTPBadRequest("Unknown form button pressed")

    return HTTPBadRequest("POST-only endpoint")
