.. _choosing-an-interpreter:

Choosing an Interpreter
=======================

The two most popular in-browser Python interpreters are Pyodide and MicroPython. Blu supports both, but uses MicroPython by default. To use Pyodide, set the interpreter in ``__settings__.py``:

.. code-block:: python
    :caption: app/__settings__.py

    INTERPRETER = 'pyodide'


Pyodide is CPython compiled to WebAssembly and has almost all the features available in other CPython distributions. MicroPython is a slim partial implementation of Python mainly used in microcontrollers. The main trade-offs are shown below:

.. list-table::
    :header-rows: 1

    * - Pyodide
      - MicroPython
    * - Implements almost all features of the Python language.
      - Implements Python 3.10, with a few additional features from later versions.
    * - Includes almost the entire Python standard library.
      - Includes a small subset of the Python standard library, with some standard library packages available to be installed.
    * - Provides Python APIs for interacting with the browser environment, as well as access to the JavaScript global scope.
      - Only provides access to the JavaScript global scope.
    * - Can have slow initial loads.
      - Initial page load is almost instant.
