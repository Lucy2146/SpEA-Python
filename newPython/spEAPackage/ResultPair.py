class ResultPair:
    def __init__(self, option: int, node):
        """
        option 1: new Steiner node was inserted --> return new Steiner node
        option 2: Steiner node was 'moved' --> return Steiner node
        option 3: Steiner node removed and rewired --> return corner node
        option 4: nothing changed --> return None
        """
        self.option = option
        self.node = node

    def getOption(self) -> int:
        return self.option

    def getNode(self):
        return self.node