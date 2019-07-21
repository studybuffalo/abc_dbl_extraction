===============================================
Alberta Blue Cross Drug Benefit List Extraction
===============================================

|BuildStatus| |Coverage| |License|

.. |BuildStatus| image:: https://travis-ci.com/studybuffalo/abc_dbl_extraction.svg?branch=master
   :target: https://travis-ci.com/studybuffalo/abc_dbl_extraction
   :alt: Travis-CI build status

.. |Coverage| image:: https://codecov.io/gh/studybuffalo/abc_dbl_extraction/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/studybuffalo/abc_dbl_extraction
   :alt: Codecov test coverage

.. |License| image:: https://img.shields.io/github/license/studybuffalo/abc_dbl_extraction.svg
   :target: https://github.com/studybuffalo/abc_dbl_extraction/blob/master/LICENSE
   :alt: License

This is a tool that scrapes the `Alberta Blue Cross Interactive Drug Benefit
List (ABC iDBL)`_ and formats it for saving in a database. This data is currently
used to power the `Drug Price Calculator`_ at `studybuffalo.com`_.

.. _Alberta Blue Cross Interactive Drug Benefit List (ABC iDBL): https://idbl.ab.bluecross.ca/idbl/load.do

.. _Drug Price Calculator: https://studybuffalo.com/tools/drug-price-calculator/

.. _studybuffalo.com: https://studybuffalo.com/

---------------
Getting Started
---------------

To get started, you will need to ensure all program dependencies are
installed. The easiest way to do this is by installing and running
everything `Pipenv`_.

.. _Pipenv: https://docs.pipenv.org/en/latest/

If you do not have Pipenv installed:

.. code:: shell

    $ pip install pipenv

You can then install all requirements:

.. code:: shell

    $ pipenv install

Once all dependencies are installed, you can run the program from the
command line:

.. code:: shell

    $ pipenv run python extract.py 0 100

In the above example, 0 and 100 are the start and end IDs,
respectively, to extract from the iDBL.

-------------
Configuration
-------------

The application is configured in two ways: the command line options and
the ``extraction.ini`` file.

Command Line Options
====================

When running the application, you **must** specify the start and end ID
as the last two arguments.

The following options are optional and also available in the command
line under the ``--help`` command:

- ``--config <path>`` (**str**): the ``path`` to an .ini file to use for configuration.
  Defaults to ``./extraction.ini``.

- ``--disable-data-upload``: Disables data upload to the API

- ``--save-html``: Saves the extracted HTML files to file.

- ``--save-api``: Saves the pre-uploaded API data to file.

- ``--use-html-file``: Uses local HTML files for data extraction,
  rather than accessing the iDBL. Typically these files would be saved
  in advance from the ``--save-html`` flag.

INI File Configuration
======================

The INI file is used to used to set required settings that change less
frequently. A sample file is provided in the repo under
``./.extraction.ini``. By default, the application looks for the file
in the root directory under ``./extraction.ini``. The following are
explanations of the available settings:

- ``[[settings]]``

  - ``crawl_delay`` (**int**): The number of seconds to wait between
    calls to the iDBL. Keep at at least 1 second to avoid triggering
    a blacklist.

  - ``api_url`` (**str**): The root URL to make API calls from.
    Include any trailing slashes (``/``) in this.

  - ``abc_url`` (**str**): The root URL to make iDBL calls from.
    Include everything before the query ``?``.

- ``[[robot]]``

  - ``user_agent`` (**str**): A User Agent string to identify the
    application with.

  - ``from`` (**str**): An email to contact you at.

- ``[[locations]]``

  - ``html`` (**str**): Path to the directory to save and retrieve
    HTML files from.

  - ``api`` (**str**): Path to the directory to save API files at.

- ``[[sentry]]``

  - ``dsn`` (**str**): the Sentry DSN to use for error reports.

-------------
Running Tests
-------------

To run tests, you will need to ensure the development dependencies are
installed. If not done already, you can do this by running:

.. code:: shell

    $ pipenv install --dev


Tests can then be run with:

.. code:: shell

    $ pipenv run pytest

Coverage is also available and can be added by including the following
flags:

.. code:: shell

    $ pipenv run --cov=. --cov-config=.coveragerc --cov-report=html

Tests can be configured with the ``.coveragerc`` file in this
repository. the ``--cov-report`` option accepts either ``xml``
(machine-readable) or ``html`` (human-readable).

-------
Authors
-------

Joshua Robert Torrance (StudyBuffalo_)

.. _StudyBuffalo: https://github.com/studybuffalo

-------
License
-------

This project is licensed under the GPLv3. Please see the LICENSE_ file for details.

.. _LICENSE: https://github.com/studybuffalo/abc_dbl_extraction/blob/master/LICENSE
