type Node = str | HTMLElement
"""
A valid child of a React element.
"""


class HTMLElement:
    """A React HTML Element."""

    def __getitem__(self, children: Node | tuple[Node, ...]) -> 'HTMLElement':
        """
        Create a copy of **self** with the specified children.

        .. code-block:: python
        
            empty_div = HTMLElement('div')  # <div />
            div_with_children = empty_div['Hello!']  # <div>Hello!</div>

        :param children: One or more React nodes.
        :return: A copy of **self** whose children are set to
            **children**.
        """
        ...