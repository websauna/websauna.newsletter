"""Newsletter admin inteface."""

# Pyramid
import colander
import deform
from pyramid import httpexceptions
from pyramid.response import Response
from pyramid.view import view_config

# Websauna
from websauna.newsletter.interfaces import INewsletterGenerator
from websauna.system.admin.admin import Admin
from websauna.system.core import messages
from websauna.system.core.utils import get_secrets
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.form.schema import CSRFSchema
from websauna.system.http import Request
from websauna.system.user.utils import get_user_class

from .mailgun import MailgunError
from .sender import send_newsletter
from .state import NewsletterState


class NewsletterSend(CSRFSchema):
    """Send a news letter."""

    subject = colander.SchemaNode(colander.String(), title="Newsletter subject")

    preview = colander.SchemaNode(colander.Boolean(), description="Is this a preview send.", default=True)

    import_subscribers = colander.SchemaNode(colander.Boolean(), description="Import userbase as new subscribers", default=True)

    email = colander.SchemaNode(colander.String(), title="Preview email", description="Send preview email to this email address", validator=colander.Email(), missing=colander.null)

    domain = colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        widget=deform.widget.TextInputWidget(readonly=True),
        title="Mailgun outbound domain",
        description="From secrets.ini",
    )

    mailing_list = colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        title="Mailgun mailing list email",
        widget=deform.widget.TextInputWidget(readonly=True),
        description="From secrets.ini",
    )

    api_key = colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        widget=deform.widget.TextInputWidget(readonly=True),
        title="Mailgun API key",
        description="From secrets.ini",
    )

    def validator(self, node: "NewsletterSend", appstruct: dict):
        """Custom schema level validation code."""

        # appstruct is Colander appstruct after all other validations have passed
        # Note that this method may not be never reached
        if appstruct["preview"] and appstruct["email"] == colander.null:
            # This error message appears at the top of the form
            raise colander.Invalid(node["email"], "Please fill in email field if you want to send a preview email.")


@view_config(context=Admin,
    name="newsletter",
    route_name="admin",
    permission="edit",
    renderer="newsletter/admin.html")
def newsletter(context: Admin, request: Request):
    """Newsletter admin form."""
    schema = NewsletterSend().bind(request=request)

    # Create a styled button with some extra Bootstrap 3 CSS classes
    b = deform.Button(name='process', title="Send", css_class="btn-block btn-lg btn-primary")
    form = deform.Form(schema, buttons=(b, ), resource_registry=ResourceRegistry(request))

    secrets = get_secrets(request.registry)
    api_key = secrets.get("mailgun.api_key", "")
    domain = secrets.get("mailgun.domain", "")
    mailing_list = secrets.get("mailgun.mailing_list", "")
    preview_url = request.resource_url(context, "newsletter-preview")

    # TODO: Use user registry here
    User = get_user_class(request.registry)
    user_count = request.dbsession.query(User).count()

    state = NewsletterState(request)

    rendered_form = None

    # User submitted this form
    if request.method == "POST":
        if 'process' in request.POST:

            try:
                appstruct = form.validate(request.POST.items())

                if appstruct["preview"]:
                    send_newsletter(request, appstruct["subject"], preview_email=appstruct["email"], import_subscribers=appstruct["import_subscribers"])
                    messages.add(request, "Preview email sent.")
                else:
                    send_newsletter(request, appstruct["subject"], import_subscribers=appstruct["import_subscribers"])
                    messages.add(request, "Newsletter sent.")

                return httpexceptions.HTTPFound(request.url)

            except MailgunError as e:
                # Do a form level error message
                exc = colander.Invalid(form.widget, "Could not sent newsletter:" + str(e))
                form.widget.handle_error(form, exc)

            except deform.ValidationFailure as e:
                # Render a form version where errors are visible next to the fields,
                # and the submitted values are posted back
                rendered_form = e.render()
        else:
            # We don't know which control caused form submission
            return httpexceptions.HTTPBadRequest("Unknown form button pressed")

    # Render initial form
    # Default values for read only fields
    if rendered_form is None:
        rendered_form = form.render({
            "api_key": api_key,
            "domain": domain,
            "mailing_list": mailing_list,
        })

    # This loads widgets specific CSS/JavaScript in HTML code,
    # if form widgets specify any static assets.
    form.resource_registry.pull_in_resources(request, form)

    return locals()


@view_config(context=Admin,
    name="newsletter-preview",
    route_name="admin",
    permission="edit")
def newsletter_preview(request: Request):
    """Render the preview of current outgoing newsletter inside an <iframe>."""

    newsletter = request.registry.queryAdapter(request, INewsletterGenerator)
    if not newsletter:
        return Response("INewsletterGenerator not configured")

    state = NewsletterState(request)

    return Response(newsletter.render(state.get_last_send_timestamp()))
