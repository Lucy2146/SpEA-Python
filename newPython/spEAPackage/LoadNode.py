import random
from .Node import Node


class LoadNode(Node):
    DUMMY = 1234.0
    #loads per user node in kWh per year

    def __init__(self, xcoord, ycoord, load=None):
        super().__init__(xcoord, ycoord)

        if load is None:
            self.load = LoadNode.DUMMY
            print("WARNING: Dummy load is used.")
        else:
            self.load = load

    # -------------------------
    # LOAD METHODS
    # -------------------------

    def setLoad(self, load):
        self.load = load

    def getLoad(self):
        return self.load

    # -------------------------
    # OPTIONAL: clone
    # -------------------------

    def clone(self):
        return LoadNode(self.x, self.y, self.load)
    

    def __hash__(self):
        return hash((self.x, self.y))


# -------------------------
# MAIN (test/demo)
# -------------------------

if __name__ == "__main__":
    n = 10
    nodes = []

    for _ in range(n):
        xcoord = random.random() * 100.0
        ycoord = random.random() * 100.0
        random_load = random.random() * 15.0 + 10.0

        nodes.append(LoadNode(xcoord, ycoord, random_load))

    for node in nodes:
        print(node.get_coords()[0], node.get_coords()[1])