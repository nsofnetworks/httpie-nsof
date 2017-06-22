===========
httpie-nsof
===========

Nsof OAuth 2 plugin for the `HTTPie <https://github.com/jkbr/httpie>`_ command line HTTP client.


Installation
------------

.. code-block:: bash

    $ python setup.py install


You should now see ``nsof`` under ``--auth-type`` in ``$ http --help`` output.


Setup
-----

.. code-block:: bash

    $ httpie-nsof-setup
    
    
Your HTTPie should be configured to use Nsof's auth plugin with your creds (see ~/.httpie/config.json).


Usage
-----

.. code-block:: bash

    $ http --auth-type=nsof GET https://api.nsof.io/v1/users
    

It's possible to pass a different effective org using the env ``EORG``:

.. code-block:: bash

    $ EORG=nsof http --auth-type=nsof GET https://api.nsof.io/v1/users
