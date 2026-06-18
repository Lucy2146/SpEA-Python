import math


class Node:
    def __init__(self, xcoord, ycoord):
        self.x = xcoord
        self.y = ycoord


    # -------------------------
    # Basic getters
    # -------------------------
    def getCoords(self):
        return [self.x, self.y]

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # -------------------------
    # Distance functions
    # -------------------------
    def distanceSqrTo(self, other):
        if self == other:
            return 0.0
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def distanceTo(self, other):
        if self == other:
            return 0.0
        dist = math.sqrt(self.distanceSqrTo(other))
        if math.isnan(dist): print("! distance to is nan")
        if math.isinf(dist): print("! distance to is inf")
        
        return dist

    # -------------------------
    # Closest point on line AB
    # -------------------------
    def closestPoint(self, a, b):
        """
        Returns [distance_squared, xcoord, ycoord]
        """

        # projection factor
        denom = (b.x - a.x) ** 2 + (b.y - a.y) ** 2

        # Handle degenerate case (a == b)
        if denom == 0:
            dist = self.distance_sqr_to(a)
            return [dist, a.x, a.y]

        r = ((self.x - a.x) * (b.x - a.x) +
             (self.y - a.y) * (b.y - a.y)) / denom

        # If projection lies on segment
        if 0.0 < r < 1.0:
            xcoord = a.x + r * (b.x - a.x)
            ycoord = a.y + r * (b.y - a.y)
            dist = (self.x - xcoord) ** 2 + (self.y - ycoord) ** 2
            return [dist, xcoord, ycoord]

        # Otherwise closest endpoint
        dist_a = self.distance_sqr_to(a)
        dist_b = self.distance_sqr_to(b)

        if dist_b < dist_a:
            return [dist_b, b.x, b.y]
        else:
            return [dist_a, a.x, a.y]

    # -------------------------
    # Equivalent to Clusterable.getPoint()
    # -------------------------
    def getPoint(self):
        return [self.x, self.y]

    # -------------------------
    # Equality (important!)
    # -------------------------
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Node(x={self.x}, y={self.y})"
    
    def __hash__(self):
        return hash((self.x, self.y))