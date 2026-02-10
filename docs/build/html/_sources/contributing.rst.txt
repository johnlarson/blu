Contributing
============

Setup
-----

1. Fork the repository on GitHub.

2. Ensure `Python 3.13 <https://www.python.org/downloads/>`_ is installed.

3. Ensure `Pipenv <https://pipenv.pypa.io>`_ is installed.

4. cd into the repository root and run ``pipenv install``.

5. Run tests with ``pipenv run pytest``. If the tests pass, you have successfully set up your development environment and are ready to make a change to the codebase.


.. todo::

    Add link to repository on GitHub


Making Changes
--------------

1. Update the :ref:`API Reference` (and :ref:`User Guide`, if appropriate) to reflect intended changes.

2. Write tests or update existing ones to test the feature or bug fix you are implementing.

3. Ensure the tests you wrote or changed fail.

4. Get all tests to pass.

5. If you haven't already, make a pull request.

Make a Pull Request Early
-------------------------

You don't have to wait until your changes are ready to merge to make a pull request. In fact, making a pull request early allows you to get early feedback, preventing you from doing significant work that is later rejected. For example, a pull request with just proposed documentation changes allows revisions to be made before anything is implemented, and a pull request with initial work allows revisions to be made to implementation stategy before more work has been put into the implementation.
