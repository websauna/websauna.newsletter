This is a newsletter addon for `Websauna framework <https://websauna.org>`_. It is intended for automatic newsletter generation from the site content.

Features
========

* Automatic newsletter generation from site content

* Admin interface for newsletter preview and send

* Import all site users as newsletter subscribers

* Outbound email through `Mailgun <http://mailgun.com/>`_

* Unsubscribe management through Mailgun

* Redis based newsletter state management (when the last letter went out, etc.)

Installation
============

To run this package you need Python 3.4+, PostgresSQL and Redis.

You need to provide your own site-specific INewsletter implementation that populates the news letter content.

Installing Python package
-------------------------

Install this package using ``pip``.

Setup newsletter renderer
-------------------------

You need to register a site specific newsletter that is responsible for rendering your newsletter HTML payload. Do this in your ``Initializer.configure_views``. Example::


        # Configure newsletter renderer
        from mysite.views.newsletter import NewsletterRenderer
        from websauna.newsletter.interfaces import INewsletterGenerator
        registry = self.config.registry
        registry.registerAdapter(factory=NewsletterRenderer, required=(IRequest,), provided=INewsletterGenerator)

For more information see ``demo.py``.

Setting up the secrets
----------------------

Add Mailgun API keys and such in ``myapp/conf/development-secrets.ini``.

Example::

    [mailgun]
    # Get from Mailgun
    api_key = x

    # What is the mailing list we use in the test suite
    mailing-list = unit-testing@mailgun.websauna.org

    # Outbound domain used for the newslettering
    domain = mailgun.websauna.org

    # From: email we use to send the newsletter
    from = newsletter-demo@websauna.org

Usage
=====

Visit Newsletter tab in the admin interface.

Local development mode
======================

Activate the virtual environment of your Websauna application.

Then::

    cd newsletter  # This is the folder with setup.py file
    pip install -e .

Running the development website
===============================

Local development machine
-------------------------

Example (OSX / Homebrew)::

    psql create newsletter_dev
    ws-sync-db websauna/newsletter/conf/development.ini
    ws-pserve websauna/newsletter/conf/development.ini --reload

Running the test suite
======================

First create test database::

    # Create database used for unit testing
    psql create newsletter_test

Install test and dev dependencies (run in the folder with ``setup.py``)::

    pip install -e ".[dev,test]"

Run test suite using py.test running::

    py.test

TODO
====

* Double confirmation to the mailing list subscription

More information
================

Please see https://websauna.org/