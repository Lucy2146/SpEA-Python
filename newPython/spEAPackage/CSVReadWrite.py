import csv
import os

from .LoadNode import LoadNode
from .ObNode import ObNode
from .Obstacle import Obstacle
from .SteinerNode import SteinerNode
from .GenomeSPOB import GenomeSPOB


class CSVreadWrite:

    FNAME_LOADS = "LoadNodes.csv"
    FNAME_EDGES = "Connections.csv"
    FNAME_OBSTACLES = "Obstacles.csv"

    HEADER_NODES = ["Xcoord", "Ycoord", "Load"]
    HEADER_TERMINALS = ["Xcoord", "Ycoord"]
    HEADER_EDGES = ["NodeID1", "NodeID2"]

    COMMA = ","

    # ============================================================
    # READ GENOME
    # ============================================================

    @staticmethod
    def read_to_genome(input_path, print_data=False):
        """
        Reads load nodes and edges into a Genome object.
        """

        nodes = CSVreadWrite.read_nodes(input_path, print_data)

        genome = GenomeSPOB(nodes)

        edges = CSVreadWrite.reading_edges(input_path, print_data)

        for edge in edges:
            genome.add_edge(edge[0], edge[1])

        return genome

    # ============================================================
    # READ EDGES
    # ============================================================

    @staticmethod
    def reading_edges(input_path, print_data=False):

        edges = []

        file_path = os.path.join(input_path, CSVreadWrite.FNAME_EDGES)

        try:
            with open(file_path, newline="") as csvfile:

                reader = csv.reader(csvfile)

                # skip header
                next(reader)

                for row in reader:

                    if len(row) < 2:
                        continue

                    try:
                        from_node = int(row[0])
                        to_node = int(row[1])

                        edge = [from_node, to_node]

                        edges.append(edge)

                        if print_data:
                            print(f"Edge from {from_node} to {to_node}")

                    except ValueError as e:
                        print(e)

        except FileNotFoundError:
            raise FileNotFoundError("Could not find edges.")

        return edges

    # ============================================================
    # READ LOAD NODES
    # ============================================================

    @staticmethod
    def read_nodes(input_path, print_data=False):

        return CSVreadWrite.read_nodes_from_file(
            input_path,
            CSVreadWrite.FNAME_LOADS,
            print_data
        )

    @staticmethod
    def read_nodes_from_file(input_path, file_name, print_data=False): 

        nodes = []

        file_path = os.path.join(input_path, file_name)
        #file_path = input_path
        try:
            with open(file_path, newline="") as csvfile:

                reader = csv.reader(csvfile)

                # skip header
                next(reader)

                node_id = 0

                for row in reader:

                    if len(row) < 2:
                        continue

                    try:
                        xcoord = float(row[0])
                        ycoord = float(row[1])

                        # with load
                        if len(row) >= 3 and row[2] != "":
                            load = float(row[2])
                            node = LoadNode(xcoord, ycoord, load)

                        # without load
                        else:
                            node = LoadNode(xcoord, ycoord)

                        nodes.append(node)

                        if print_data:
                            print(
                                f"Node {node_id} with coordinates: "
                                f"[{node.get_x()}, {node.get_y()}] "
                                f"and load: {node.get_load()}"
                            )

                        node_id += 1

                    except ValueError as e:
                        print(e)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find {file_path}"
            )

        return nodes

    # ============================================================
    # READ OBSTACLES
    # ============================================================

    @staticmethod
    def read_obstacles(input_path, print_data=False):

        return CSVreadWrite.read_obstacles_from_file(
            input_path,
            CSVreadWrite.FNAME_OBSTACLES,
            print_data
        )

    @staticmethod
    def read_obstacles_from_file(
        input_path,
        file_name,
        print_data=False
    ):

        obstacles = []

        file_path = os.path.join(input_path, file_name)

        try:
            with open(file_path, "r") as f:

                lines = [line.rstrip("\n") for line in f]

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find {file_name}"
            )

        if len(lines) == 0:
            print("WARNING: Empty obstacle input file.")
            return []

        current_nodes = []

        obstacle_nr = 0
        solid = True
        cross_cost = 0.0

        i = 0

        while i < len(lines):

            line = lines[i].strip()

            # skip empty lines
            if line == "":
                i += 1
                continue

            # ----------------------------------------------------
            # obstacle type line
            # ----------------------------------------------------

            obstacle_nr += 1

            cc = line.split(",")[0]

            if cc.lower() == "max":
                solid = True
                type_ob = "Solid Obstacle"

            else:
                solid = False
                type_ob = "Soft Obstacle"

                try:
                    cross_cost = float(cc)

                except ValueError as e:
                    print(e)

            current_nodes = []

            if print_data:
                print(
                    f"{type_ob} number {obstacle_nr} "
                    f"with node coordinates:"
                )

            i += 1

            # ----------------------------------------------------
            # read obstacle nodes
            # ----------------------------------------------------

            while i < len(lines):

                line = lines[i].strip()

                # end of obstacle
                if line == "" or line == ",":
                    break

                fields = line.split(",")

                try:
                    xcoord = float(fields[0])
                    ycoord = float(fields[1])

                    node = ObNode(xcoord, ycoord)

                    current_nodes.append(node)

                    if print_data:
                        print(f"[{node.get_x()}, {node.get_y()}]")

                except ValueError as e:
                    print(e)

                i += 1

            # create obstacle
            obstacle = Obstacle(current_nodes)

            if not solid:
                obstacle.makeSoft(cross_cost)

            obstacles.append(obstacle)

            i += 1

        if print_data:
            print(f"There were {len(obstacles)} obstacles added.\n")

        return obstacles

    # ============================================================
    # READ STEINER NODES
    # ============================================================

    @staticmethod
    def read_steiners(input_path, file_name, print_data=False):

        nodes = []

        file_path = os.path.join(input_path, file_name)

        try:
            with open(file_path, newline="") as csvfile:

                reader = csv.reader(csvfile)

                # skip header
                next(reader)

                node_id = 0

                for row in reader:

                    if len(row) < 2:
                        continue

                    try:
                        xcoord = float(row[0])
                        ycoord = float(row[1])

                        node = SteinerNode(xcoord, ycoord)

                        nodes.append(node)

                        if print_data:
                            print(
                                f"Node {node_id} with coordinates: "
                                f"[{node.get_x()}, {node.get_y()}]"
                            )

                        node_id += 1

                    except ValueError as e:
                        print(e)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not find {file_name}"
            )

        return nodes

    # ============================================================
    # WRITE GENOME INPUT
    # ============================================================

    def write_input(self, input_path, genome):

        assert len(genome.get_steiner_nodes()) == 0, (
            "You cannot store Steiner points yet!"
        )

        # write nodes
        self.write_nodes(
            input_path,
            genome.get_load_nodes()
        )

        # write edges
        file_path = os.path.join(
            input_path,
            self.FNAME_EDGES
        )

        with open(file_path, "w", newline="") as csvfile:

            writer = csv.writer(csvfile)

            writer.writerow(self.HEADER_EDGES)

            for edge in genome.get_all_edges():
                writer.writerow([edge[0], edge[1]])

        print(f"Edges have been printed to {self.FNAME_EDGES}")

    # ============================================================
    # WRITE LOAD NODES
    # ============================================================

    @staticmethod
    def write_nodes(input_path, load_nodes):

        CSVreadWrite.write_nodes_to_file(
            input_path,
            CSVreadWrite.FNAME_LOADS,
            load_nodes
        )

    @staticmethod
    def write_nodes_to_file(
        input_path,
        file_name,
        load_nodes,
        with_loads=True
    ):

        file_path = os.path.join(input_path, file_name)

        with open(file_path, "w", newline="") as csvfile:

            writer = csv.writer(csvfile)

            if with_loads:
                writer.writerow(CSVreadWrite.HEADER_NODES)
            else:
                writer.writerow(CSVreadWrite.HEADER_TERMINALS)

            for node in load_nodes:

                if with_loads:
                    writer.writerow([
                        node.get_x(),
                        node.get_y(),
                        node.get_load()
                    ])

                else:
                    writer.writerow([
                        node.get_x(),
                        node.get_y()
                    ])

        print(f"\nNodes have been printed to {file_name}")

    @staticmethod
    def write_terminals(input_path, file_name, load_nodes):

        CSVreadWrite.write_nodes_to_file(
            input_path,
            file_name,
            load_nodes,
            with_loads=False
        )

    # ============================================================
    # WRITE OBSTACLES
    # ============================================================

    @staticmethod
    def write_obstacles(input_path, obstacles):

        CSVreadWrite.write_obstacles_to_file(
            input_path,
            CSVreadWrite.FNAME_OBSTACLES,
            obstacles
        )

    @staticmethod
    def write_obstacles_to_file(
        input_path,
        file_name,
        obstacles
    ):

        file_path = os.path.join(input_path, file_name)

        with open(file_path, "w") as f:

            for i, obstacle in enumerate(obstacles):

                if obstacle.is_solid():
                    cross_cost = "max"
                else:
                    cross_cost = str(
                        obstacle.get_cross_costs()
                    )

                f.write(cross_cost + "\n")

                for node in obstacle.get_points():

                    line = (
                        f"{node.get_x()},"
                        f"{node.get_y()}"
                    )

                    f.write(line + "\n")

                # blank line between obstacles
                if i < len(obstacles) - 1:
                    f.write("\n")

        print(f"\nObstacles have been printed to {file_name}")

    # ============================================================
    # WRITE OUTPUT
    # ============================================================

    @staticmethod
    def write_output(output_file, content, create_new_file=True):

        mode = "w" if create_new_file else "a"

        with open(output_file, mode) as f:
            f.write(str(content))