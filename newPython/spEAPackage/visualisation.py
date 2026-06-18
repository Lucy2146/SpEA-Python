import matplotlib.pyplot as plt
from shapely.geometry import LineString

from .geometry import weighted_edge_length


def plot_instance(terminals, obstacles):

    fig, ax = plt.subplots()

    # plot terminals
    xs = [p[0] for p in terminals]
    ys = [p[1] for p in terminals]

    ax.scatter(xs, ys, c="blue", label="Terminals")

    # plot obstacles
    for obs in obstacles:

        xs = [p[0] for p in obs.vertices] + [obs.vertices[0][0]]
        ys = [p[1] for p in obs.vertices] + [obs.vertices[0][1]]

        if obs.solid:
            ax.fill(xs, ys, color="black", alpha=0.5, label="Solid obstacle")
        else:
            ax.fill(xs, ys, color="orange", alpha=0.4, label="Soft obstacle")

    ax.set_aspect("equal")
    ax.set_title("Input Instance")

    plt.show()


def compute_mst_edges(nodes, obstacles):

    import heapq

    n = len(nodes)

    visited = [False]*n
    visited[0] = True

    edges = []

    heap = []

    for i in range(1, n):

        w = weighted_edge_length(nodes[0], nodes[i], obstacles)

        heapq.heappush(heap,(w,0,i))

    mst = []

    while heap:

        w,u,v = heapq.heappop(heap)

        if visited[v]:
            continue

        if w == float("inf"):
            return []

        visited[v] = True

        mst.append((u,v))

        for k in range(n):

            if not visited[k]:

                heapq.heappush(
                    heap,
                    (weighted_edge_length(nodes[v],nodes[k],obstacles),v,k)
                )

    return mst


def plot_solution(best, terminals, obstacles, obstacle_corners):

    fig, ax = plt.subplots()

    # plot obstacles
    for obs in obstacles:

        xs = [p[0] for p in obs.vertices] + [obs.vertices[0][0]]
        ys = [p[1] for p in obs.vertices] + [obs.vertices[0][1]]

        if obs.solid:
            ax.fill(xs, ys, color="black", alpha=0.5)
        else:
            ax.fill(xs, ys, color="orange", alpha=0.4)

    nodes = terminals.copy()

    nodes.extend(best.steiner_points)

    for bit, corner in zip(best.obstacle_bits, obstacle_corners):

        if bit == 1:
            nodes.append(corner)

    # MST edges
    mst_edges = compute_mst_edges(nodes, obstacles)

    for u,v in mst_edges:

        p1 = nodes[u]
        p2 = nodes[v]

        ax.plot(
            [p1[0],p2[0]],
            [p1[1],p2[1]],
            c="green"
        )

    # terminals
    tx = [p[0] for p in terminals]
    ty = [p[1] for p in terminals]

    ax.scatter(tx, ty, c="blue", label="Terminals")

    # Steiner points
    sx = [p[0] for p in best.steiner_points]
    sy = [p[1] for p in best.steiner_points]

    ax.scatter(sx, sy, c="red", label="Steiner")

    ax.set_aspect("equal")
    ax.set_title("Best Steiner Tree")

    plt.legend()

    plt.show()