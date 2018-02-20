# Pyramid
from pyramid.config import Configurator

# Websauna
from websauna.system import Initializer
from websauna.utils.autoevent import after
from websauna.utils.autoevent import bind_events


class AddonInitializer:
    """Configure this addon for websauna.

    * We hook to existing parts of initialization process using ``@after`` aspect advisor

    * For something we don't have a direct join point we just initialize through ``run()``
    """

    def __init__(self, config: Configurator):
        self.config = config

    @after(Initializer.configure_templates)
    def configure_templates(self):
        """Include our package templates folder in Jinja 2 configuration."""
        # Use prepend=False here so that the app can override our templates easily
        self.config.add_jinja2_search_path('websauna.newsletter:templates', name='.html', prepend=False)  # HTML templates for pages

    @after(Initializer.configure_tasks)
    def configure_tasks(self):
        from . import tasks
        self.config.scan(tasks)

    @after(Initializer.configure_admin)
    def configure_admin(self):
        from . import adminviews
        from . import menu
        self.config.scan(adminviews)
        self.config.scan(menu)

    def configure_addon_views(self):
        from . import views
        self.config.scan(views)

    def run(self):

        # This will make sure our initialization hooks are called later
        bind_events(self.config.registry.initializer, self)

        # Run our custom initialization code which does not have a good hook
        self.configure_addon_views()


def includeme(config: Configurator):
    """Entry point for Websauna main app to include this addon.

    In the Initializer of your app you should have:

        def include_addons(self):
            # ...
            self.config.include("websauna.newsletter")

    """
    addon_init = AddonInitializer(config)
    addon_init.run()
