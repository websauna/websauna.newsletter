# Pyramid
from pyramid.events import subscriber

# Websauna
from websauna.system.admin.events import AdminConstruction
from websauna.system.admin.menu import TraverseEntry


@subscriber(AdminConstruction)
def contribute_model_admin(event):
    """Create newsletter menu entry in the admin interface."""

    admin = event.admin

    menu = admin.get_admin_menu()
    entry = TraverseEntry("admin-menu-newsletter", label="Newsletter", resource=admin, name="newsletter", icon="fa-envelope")
    menu.add_entry(entry)
