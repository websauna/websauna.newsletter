from websauna.system.http import Request
from websauna.system.core.route import simple_route


# Configure a sample view provided by this addon
@simple_route("/example-view", route_name="example", renderer='newsletter/example.html')
def example_view(request: Request):
    """Render site homepage."""
    return {"project": "newsletter"}
