"""This contains app entry point for running a demo site for this addon or running functional tests for this addon."""

import websauna.system
from pyramid.interfaces import IRequest
from pyramid.renderers import render

from websauna.newsletter.interfaces import INewsletterGenerator
from websauna.system.http import Request
from zope.interface import implementer


@implementer(INewsletterGenerator)
class DemoNewsletterRenderer:
    """Render sample newsletter content."""

    def __init__(self, request: Request):
        self.request = request

    def render(self):
        """Render some sample content."""
        from websauna.system.user.models import User
        request = self.request
        users = request.dbsession.query(User).all()
        return render("newsletter/demo_newsletter.html", value={"users": users}, request=self.request)


class Initializer(websauna.system.DemoInitializer):
    """A demo / test app initializer for testing addon websauna.newsletter."""

    def include_addons(self):
        """Include this addon in the configuration."""
        self.config.include("websauna.newsletter")

    def run(self):
        super(Initializer, self).run()

        # Configure newsletter renderer
        registry = self.config.registry
        registry.registerAdapter(factory=DemoNewsletterRenderer, required=(IRequest,), provided=INewsletterGenerator)


def main(global_config, **settings):
    init = Initializer(global_config)
    init.run()
    return init.make_wsgi_app()
