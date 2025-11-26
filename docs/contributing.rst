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

1. Update the :ref:`API Reference` to reflect intended changes. The :ref:`API Reference` should be treated as the single source of truth for requirements; any expected functionality should be documented there.

2. As appropriate, update the :ref:`User Guide` to reflect intended changes. This will be necessary if the change invalidates part of the :ref:`User Guide`, is difficult to understand with the :ref:`API Reference` alone, or affects core functionality.

3. Update tests to reflect changes to :ref:`API Reference`. These tests ensure the package works as expected.

4. As necessary, update the User Guide tests to reflect changes made to the :ref:`User Guide`. This will be necessary if you made changes to code examples in the User Guide or added new code examples. These tests ensure the User Guide is accurate.

5. Ensure the tests you wrote or changed fail.

6. Get all tests to pass.

7. If you haven't already, make a pull request.

Make a Pull Request Early
-------------------------

You don't have to wait until your changes are ready to merge to make a pull request. In fact, making a pull request early allows you to get early feedback, preventing you from doing significant work that is later rejected. For example, a pull request with just proposed documentation changes allows revisions to be made before anything is implemented, and a pull request with initial work allows revisions to be made to implementation stategy before more work has been put into the implementation.

End-to-End Tests
----------------

If you submit a pull request that changes core functionality or the way elements are rendered to the DOM, you may be asked to update end-to-end tests to reflect these changes. Generally, you should assume this is not necessary, but know that it may be requested after you make a pull request.