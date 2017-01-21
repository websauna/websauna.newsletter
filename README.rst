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

Local development mode
----------------------

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

Create ``websauna/newsletter/conf/development-secrets.ini``.

Content::

    # Secrets for running a demo site

    [authentication]
    # This is a secret seed used in email login
    secret = x

    [authomatic]
    # This is a secret seed used in various OAuth related keys
    secret = x

    # The secret used to hash session keys
    [session]
    secret = x

    # get from Mailgun account settings
    [mailgun]
    api_key = key-xxx

    # What is the mailing list we use in the test suite
    # Automatically creatd
    test-suite-mailing-list = unit-testing@websauna.org


First create test database::

    # Create database used for unit testing
    psql create newsletter_test

Install test and dev dependencies (run in the folder with ``setup.py``)::

    pip install -e ".[dev,test]"

Run test suite using py.test running::

    py.test

More information
================

Please see https://websauna.org/