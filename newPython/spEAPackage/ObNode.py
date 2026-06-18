from .Node import Node

class ObNode(Node):
    """
    This class is for obstacle nodes
    """

    def __init__(self, xcoord, ycoord):
        super().__init__(xcoord, ycoord)

    def clone(self):
        """
        Creates a deep copy of this obstacle node
        """
        return ObNode(self.x, self.y)
    
    def __hash__(self):
        return hash((self.x, self.y))