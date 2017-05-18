===========
httpie-nsof
===========

Nsof OAuth 2 plugin for the `HTTPie <https://github.com/jkbr/httpie>`_ command line HTTP client.


Installation
------------

.. code-block:: bash

    $ python setup.py install


You should now see ``nsof`` under ``--auth-type`` in ``$ http --help`` output.


Usage
-----

.. code-block:: bash

    $ http --auth-type=nsof --auth='org/username:password' https://api.nsof.io/v1/users


You can also use `HTTPie sessions <https://httpie.org/doc#sessions>`_:

.. code-block:: bash

    # Create session
    $ http --session=logged-in --auth-type=nsof --auth='org/username:password' https://api.nsof.io/v1/users

    # Re-use auth
    $ http --session=logged-in POST https://api.nsof.io/v1/users


You can set the default ``--auth-type=nsof`` option in the ``~/.httpie/config.json`` file for convenience:

.. code-block:: bash

    $ echo '{"default_options": ["--auth-type=nsof"]}' > ~/.httpie/config.json
    $ http -a org/username:password https://api.nsof.io/v1/users


You can also set your org, username, password as default:

.. code-block:: bash

    $ echo '{"default_options": ["--auth-type=nsof", "--auth=nsof/username:password"]}' > ~/.httpie/config.json
    $ http https://api.nsof.io/v1/users


It's possible to pass a different effective org using the env ``EORG``:

.. code-block:: bash

    $ EORG=nsof http https://api.nsof.io/v1/users
