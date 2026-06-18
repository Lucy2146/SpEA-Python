import csv
from shapely.geometry import Polygon
from shapely.prepared import prep


'''class Obstacle:

    def __init__(self, weight, vertices):

        # clean input
        weight = weight.strip().replace(",", "")

        if weight.lower() == "max":
            self.weight = float("inf")
            self.solid = True
        else:
            self.weight = float(weight)
            self.solid = False

        self.vertices = vertices

        from shapely.geometry import Polygon
        from shapely.prepared import prep

        self.polygon = Polygon(vertices)
        self.prepared = prep(self.polygon)
'''
def read_terminals(path):

    terminals = []

    with open(path) as f:
        reader = csv.DictReader(f)

        for row in reader:
            terminals.append(
                (float(row["Xcoord"]), float(row["Ycoord"]))
            )

    return terminals


def read_obstacles(path):

    obstacles = []
    vertices = []
    weight = None

    with open(path) as f:

        for line in f:

            line = line.strip()

            if line == "":

                if vertices:
                    obstacles.append(Obstacle(weight, vertices))

                vertices = []
                weight = None
                continue

            if weight is None:

                weight = line

            else:

                parts = line.replace(",", " ").split()

                if len(parts) >= 2:
                    x = float(parts[0])
                    y = float(parts[1])
                    vertices.append((x, y))

                vertices.append((x, y))

    if vertices:
        obstacles.append(Obstacle(weight, vertices))

    return obstacles


def collect_obstacle_corners(obstacles):

    corners = []

    for o in obstacles:
        corners.extend(o.vertices)

    return corners