``blu``
=======

.. todo::

    Document the following:

    - HTMLElement
    - Key
    - Node
    - Ref
    - Response
    - WrongEnvironmentError
    - app
    - client
    - create_rare_html_element
    - html
    - is_client
    - use_effect
    - use_state
    - use_ref 

.. automodule:: blu
    :exclude-members: HTMLElement, ClientElement

    .. autoclass:: ClientElement()
        :special-members: __call__, __getitem__

    .. autoclass:: HTMLElement()
        :special-members: __call__, __getitem__


.. py:type:: Node
    :canonical: HTMLElement | str

    A valid child of a React element.