type Node = str | HTMLElement


class HTMLElement:

    def __getitem__(self, key: Node | tuple[Node, ...]) -> 'HTMLElement':
        ...