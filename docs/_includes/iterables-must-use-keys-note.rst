.. note::

    Items in :py:class:`Iterable <collections.abc.Iterable>` children (other than :py:class:`str`\ s and :py:class:`tuple`\ s) must be keyed:

    .. code-block::

        from blu import Key
        from blu.html import div

        PEOPLE = [
            {'id': 0, 'name': 'Ana'},
            {'id': 1, 'name': 'Bill'},
            {'id': 2, 'name': 'Charlotte'},
        ]

        # Wrong!
        div[
            [
                div[f'Hello, {person["name"]}!']
                for person in PEOPLE
            ],
        ]

        # Right.
        div[
            [
                div(key=person['id'])[f'Hello, {person["name"]}!']
                for person in PEOPLE
            ],
        ]

        # Wrong!
        div[
            [f'Hello, {person["name"]}!' for person in PEOPLE],
        ]

        # Right.
        div[
            [
                Key(person["id"])[
                    f'Hello, {person["name"]}',
                ]
                for person in PEOPLE
            ],
        ]

        # Right.
        div[
            (
                'Hello, Ana!',
                'Hello, Bill!',
                'Hello, Charlotte!',
            ),
        ]

        # Right.
        div['Hello, Ana! Hello, Bill! Hello, Charlotte!']

    The rationale here is that, in :ref:`client-side rendering <Client-Side Rendering>`, items in a sequence may be moved around in response to user interaction. Giving keys to these items allows React to maintain state and render efficiently even when an item's position in a sequence changes.