from .Node import Node

class SteinerNode(Node):
    """
    This class is specifically for real Steiner points in an Euclidean Steiner minimum tree,
    i.e. degree = 3 and angles are 120.
    It should not be used for other types of Steiner points such as obstacle edge nodes.
    """

    def __init__(self, xcoord, ycoord):
        super().__init__(xcoord, ycoord)

    def move(self, xmove, ymove):
        """
        Moves the Steiner point in the given direction
        """
        self.x += xmove
        self.y += ymove

    def setNewLocation(self, x_new, y_new):
        """
        Sets a new location for this Steiner point
        """
        self.x = x_new
        self.y = y_new

    def clone(self):
        """
        Creates a deep copy of this Steiner node
        """
        return SteinerNode(self.x, self.y)