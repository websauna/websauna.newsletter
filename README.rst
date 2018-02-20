This is a newsletter addon for `Websauna framework <https://websauna.org>`_. It is intended for automatic newsletter generation from the site content.

.. contents:: :local:

Features
========

* Automatic newsletter generation from site content

* Admin interface for newsletter preview and send

* Import all site users as newsletter subscribers

* Outbound email through `Mailgun <http://mailgun.com/>`_

* Unsubscribe management through Mailgun

* Redis based newsletter state management (when the last letter went out, etc.)

* Websauna's Celery based task subsystem is used to run long running operations asynchronously

Installation
============

To run this package you need Python 3.4+, PostgresSQL and Redis.

You need to provide your own site-specific INewsletter implementation that populates the news letter content.

Installing Python package
-------------------------

Install this package using ``pip``.

Setup newsletter renderer
-------------------------

You need to register a site specific newsletter that is responsible for rendering your newsletter HTML payload. Do this in your ``Initializer.configure_views``. Example:

.. code-block:: python

        # Configure newsletter renderer
        from mysite.views.newsletter import NewsletterRenderer
        from websauna.newsletter.interfaces import INewsletterGenerator
        registry = self.config.registry
        registry.registerAdapter(factory=NewsletterRenderer, required=(IRequest,), provided=INewsletterGenerator)

For more information see ``demo.py``.

Unsubscription link
-------------------

In your renderer HTML code you can use Mailgun unsubscription management:

.. code-block:: html

  <p class="details">
    {# For Mailgun #}
    <a href="%mailing_list_unsubscribe_url%">Unsubscribe from TokenMarket newsletter.</a>
  </p>

Setting up the secrets
----------------------

Add Mailgun API keys and such in ``myapp/conf/development-secrets.ini``.

Example:

.. code-block:: ini

    [mailgun]
    # Get from Mailgun
    api_key = x

    # What is the mailing list we use in the test suite
    mailing_list = unit-testing@mailgun.websauna.org

    # Outbound domain used for the newslettering
    domain = mailgun.websauna.org

    # From: email we use to send the newsletter
    from = MyApp Newsletter <newsletter-demo@websauna.org>

Create Mailgun mailing list object
----------------------------------

Easiest to do this through ``ws-shell`` using production configuraition::

    ws-shell tokenmarket/conf/production.ini

Then using ``%cpaste`` notebook shell command::

    from websauna.system.core.utils import get_secrets
    from websauna.newsletter.mailgun import Mailgun
    secrets = get_secrets(request.registry)
    list_address = secrets["mailgun.mailing_list"]
    mailgun = Mailgun(request.registry)
    mailgun.create_list(list_address, "MyApp newsletter")

You get a reply::

    {'list': {'access_level': 'readonly',
      'address': 'newsletter@example.com',
      'created_at': 'Wed, 25 Jan 2017 17:08:56 -0000',
      'description': 'TokenMarket newsletter',
      'members_count': 0,
      'name': ''},
     'message': 'Mailing list has been created'}

Integration subscription for on your site
-----------------------------------------

A boostrap based mini subscription form is provided with the packag. It is ideal e.g. to place in the site footer.

Simply in your template do::

    <h3>Follow</h3>
    {% include "newsletter/subscription_form.html" %}


For more information run the demo and view ``demotemplates/site/footer.html``.

Usage
=====

Sending and preview
-------------------

Visit *Newsletter* tab in the admin interface to preview and send out newsletters.

Resetting the news collection date
----------------------------------

You can manually set the newsletter state, when the last newsletter was sent, from shell:

.. code-block:: python

    import datetime
    from websauna.newsletter.state import NewsletterState

    state = NewsletterState(request)
    state.set_last_send_timestamp(datetime.datetime(2016, 12, 24).replace(tzinfo=datetime.timezone.utc))

State is managed in Redis.

Exporting subscribers
---------------------

In console:

.. code-block:: python

    from websauna.system.core.utils import get_secrets
    from websauna.newsletter.mailgun import Mailgun
    secrets = get_secrets(request.registry)
    list_address = secrets["mailgun.mailing_list"]
    mailgun = Mailgun(request.registry)
    print(mailgun.list_members(list_address))  # TODO: pagination

Importing email subscribers
---------------------------

Note that importing website users is supported in the admin interface.

Example:

.. code-block:: python

    subscribers = """
    mikko@example.com
    pete@example.com
    """

    from websauna.system.core.utils import get_secrets
    from websauna.newsletter.mailgun import Mailgun
    from websauna.newsletter.views import subscribe_email

    secrets = get_secrets(request.registry)
    list_address = secrets["mailgun.mailing_list"]
    mailgun = Mailgun(request.registry)

    for s in subscribers.split():
        s = s.strip()
        if s:
            subscribe_email(request, s)

Local development mode
======================

You can development this addon locally.

Activate the virtual environment of your Websauna application.

Then:

.. code-block:: console

    cd newsletter  # This is the folder with setup.py file
    pip install -e .
    psql create newsletter_dev
    ws-sync-db  ws://websauna/newsletter/conf/development.ini
    pserve  ws://websauna/newsletter/conf/development.ini --reload

Running the test suite
======================

First create test database::

    # Create database used for unit testing
    psql create newsletter_test

Install test and dev dependencies (run in the folder with ``setup.py``)::

    pip install -e ".[dev,test]"

Run test suite using py.test running::

    py.test

Manually testing with Celery
----------------------------

Make sure Celery is not eager in ``development.ini``::

    websauna.celery_config =
        {
            "broker_url":  "redis://localhost:6379/15",
            "task_always_eager": False,
        }

Start demo (Terminal 1)::

    pserve ws://websauna/newsletter/conf/development.ini

Start Celery (Terminal 2)::

    ws-celery  ws://websauna/newsletter/conf/development.ini -- worker




TODO
====

    * Double confirmation to the mailing list subscription

More information
================

Please see https://websauna.org/