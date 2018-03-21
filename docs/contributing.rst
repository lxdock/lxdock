Contributing to LXDock
======================

Here are some simple rules & tips to help you contribute to LXDock. You can contribute in many ways!

Contributing code
-----------------

The preferred way to contribute to LXDock is to submit pull requests to the `project's Github
repository <https://github.com/lxdock/lxdock>`_. Here are some general tips regarding pull requests.

.. warning::

  Keep in mind that you should propose new features on the `project's issue tracker
  <https://github.com/lxdock/lxdock/issues>`_ before starting working on your ideas!

Development environment
#######################

You should first fork the `LXDock's repository <https://github.com/lxdock/lxdock>`_ and make sure
that `LXD <https://www.ubuntu.com/cloud/lxd>`_ is properly installed on your system. Then you can
get a working copy of the project using the following commands (eg. using Python 3.6):

.. code-block:: bash

  $ git clone git@github.com:<username>/lxdock.git
  $ cd lxdock
  $ python3.6 -m venv ./env && . ./env/bin/activate
  $ make install

Instead of setting up an environment directly on your development machine itself,
you can also use the included Vagrantfile for creating a test environment:

.. code-block:: bash

  $ vagrant up
  $ vagrant ssh
  $ make coverage

Coding style
############

Please make sure that your code is compliant with the
`PEP8 style guide <https://www.python.org/dev/peps/pep-0008/>`_. You can ignore the "Maximum Line
Length" requirement but the length of your lines should not exceed 100 characters. Remember that
your code will be checked using `flake8 <https://pypi.python.org/pypi/flake8>`_ and
`isort <https://pypi.python.org/pypi/isort/4.2.5>`_. You can use the following commands to perform
these validations:

.. code-block:: bash

  $ make lint
  $ make isort

Or:

.. code-block:: bash

  $ tox -e lint
  $ tox -e isort

Tests
#####

You should not submit pull requests without providing tests. LXDock relies on
`pytest <http://pytest.org/latest/>`_: py.test is used instead of unittest for its test runner but
also for its syntax. So you should write your tests using `pytest <http://pytest.org/latest/>`_
instead of unittest and you should not use the built-in ``TestCase``.

You can run the whole test suite using the following command:

.. code-block:: bash

  $ py.test

Code coverage should not decrease with pull requests but in some cases we
realise that isn't always possible. If this happen it should be discussed on
a Github issue with the maintainers, so that there is a record of it.

You can easily get the code coverage of the project using the following command:

.. code-block:: bash

  $ make coverage

Using the issue tracker
-----------------------

You should use the `project's issue tracker <https://github.com/lxdock/lxdock/issues>`_ if you've
found a bug or if you want to propose a new feature. Don't forget to include as many details as
possible in your tickets (eg. tracebacks if this is appropriate).
