===============================================
Alberta Blue Cross Drug Benefit List Extraction
===============================================

|BuildStatus|_ |Coverage|_ |License|_

.. |BuildStatus| image:: https://img.shields.io/jenkins/s/https/ci.studybuffalo.com/job/abc_dbl_extraction/job/master.svg
   :alt: Jenkins build status
   
.. _BuildStatus: https://ci.studybuffalo.com/blue/organizations/jenkins/abc_dbl_extraction/

.. |Coverage| image:: https://badges.ci.studybuffalo.com/coverage/abc_dbl_extraction/job/master
   :alt: Code coverage
   
.. _Coverage: https://ci.studybuffalo.com/job/abc_dbl_extraction/job/master/lastBuild/cobertura/

.. |License| image:: https://img.shields.io/github/license/studybuffalo/abc_dbl_extraction.svg
   :alt: License

.. _License: https://github.com/studybuffalo/abc_dbl_extraction/blob/master/LICENSE


This is a tool that scrapes the `Alberta Blue Cross Interactive Drug Benefit 
List (ABC iDBL)`_ and formats it for saving in a database. This data is currently
used to power the `Drug Price Calculator`_ at `studybuffalo.com`_.

.. _Alberta Blue Cross Interactive Drug Benefit List (ABC iDBL): https://idbl.ab.bluecross.ca/idbl/load.do

.. _Drug Price Calculator: https://studybuffalo.com/tools/drug-price-calculator/

.. _studybuffalo.com: https://studybuffalo.com/

Getting Started
---------------

TODO: Add instructions on running program


Unit tests for this application can be run via the standard pytest commands:

.. code:: shell

  # Standard testing
  > pipenv run py.test tests/

  # Tests with coverage reporting (HTML)
  > pipenv run py.test --cov=modules --cov-report=html tests/

  # Tests with JUnit reporting
  > pipenv run py.test --junitxml=reports/tests.xml tests/

All reports can be placed in the reports folder, whose contents are excluded
from source control.

Authors
-------

Joshua Robert Torrance (StudyBuffalo_)

.. _StudyBuffalo: https://github.com/studybuffalo

License
-------

This project is licensed under the GPLv3. Please see the LICENSE_ file for details.

.. _LICENSE: https://github.com/studybuffalo/abc_dbl_extraction/blob/master/LICENSE
