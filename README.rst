===========
httpie-nsof
===========

Nsof OAuth 2 plugin for the `HTTPie <https://github.com/jkbr/httpie>`_ command line HTTP client.


Installation
------------

.. code-block:: bash

    $ pip install httpie-nsof


You should now see ``nsof`` under ``--auth-type`` in ``$ http --help`` output.


Setup
-----

.. code-block:: bash

    $ httpie-nsof-setup
    
    
Configure Nsof's auth plugin with your creds (saved in ~/.httpie/config.json).
The credentials can be either a username/password or API Key ID/API Key Secret

Notes:
    - if username is not provided in conf file it will be searched at HTTPIE_NSOF_USERNAME
    - if password is not provided in conf file it will be searched at HTTPIE_NSOF_PASSWORD
    - manually inputted username/password supersede conf file and environment variables


Usage
-----

.. code-block:: bash

    $ http --auth-type=nsof GET https://api.nsof.io/v1/users
    

It's possible to pass a different effective org using the env ``EORG``:

.. code-block:: bash

    $ EORG=nsof http --auth-type=nsof GET https://api.nsof.io/v1/users
