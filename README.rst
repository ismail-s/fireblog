Fireblog
==================
.. image:: https://travis-ci.org/ismail-s/fireblog.svg?branch=develop
  :target: https://travis-ci.org/ismail-s/fireblog

.. image:: https://coveralls.io/repos/ismail-s/fireblog/badge.svg?branch=develop&service=github
  :target: https://coveralls.io/github/ismail-s/fireblog?branch=develop

A simple blog, written in Python, using the
`Pyramid web framework <https://www.github.com/pylons/pyramid>`_. For a live
version, see `my blog <https://blog.ismail-s.com>`_.

Getting Started
---------------

First make sure there is a running local instance of `redis <http://redis.io>`_.
Then run the following commands:

.. code:: bash

  git clone https://github.com/ismail-s/fireblog.git
  cd fireblog
  pip install -r requirements.txt
  python setup.py develop
  initialize_fireblog_db development.ini
  uwsgi --ini-paste-logged development.ini

Do note when running those commands that:

- you use a `virtualenv <https://virtualenv.pypa.io/en/latest/>`_
- You don't use development.ini when running in production.
  This is because development.ini enables the debug toolbar, which allows
  arbitrary code execution. For a warning of what this could result in, see
  `this article <http://arstechnica.co.uk/security/2015/10/patreon-was-warned-of-serious-website-flaw-5-days-before-it-was-hacked/>`_.

- If you want to run the server in production mode as a daemon, then run:

.. code:: bash

  uwsgi --ini-paste-logged production.ini

If you wish to customise stuff, eg use a database like postgres instead of
sqlite (the default), then change the .ini file you pass to these commands.

Managing the database
---------------------

The `initialize_fireblog_db` script does 3 things when run:

1) Creates the db with the required tables if they don't exist already
2) Updates the db to the latest version if necessary
3) Creates a first post if no posts exist already
4) Makes sure all required settings are in the settings table, prompting the
   user of the script to input values if a value doesn't exist or is invalid.

This means that this script doesn't accept any parameters besides the ini
file which says where the db is. The script is also safe to run at any
point, to either create, update or check the db.
