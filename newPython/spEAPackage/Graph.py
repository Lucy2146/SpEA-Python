import math
import time
from collections import defaultdict, deque
import random
import matplotlib.pyplot as plt
import os

from .LoadNode import LoadNode
from .SteinerNode import SteinerNode
from .ObNode import ObNode
from .ResultPair import ResultPair

class Graph:
    ANGLE120 = 2.0 * math.pi / 3.0
    TAN120 = -math.sqrt(3.0) #tangent of 120 deg
    TOLERANCE = 1e-6 #tolerance of rounding errors for inserting Steiner Points

    shortestPaths = None
    warningPrinted = False
    numberSPcalcs = 0
    callsToSP = 0
    nonloads = 0
    #fixed nodes?

    def __init__(self, nodes, obstacles):
        assert obstacles is not None, "Object can't be null."

        if not Graph.warningPrinted and self.shortestPaths is not None:
            print("\nWarning: In graph class the 'shortestPaths' storage is not empty on construction of a new graph.\n")
            Graph.warningPrinted = True
            try:
                time.sleep(3)
            except Exception as e:
                print(e)
                print("Sleep did not work.")

        # adjacency list: {int: [int, int, ...]}
        self.adjList = defaultdict(list)

        # copy nodes
        self.nodes = list(nodes)

        # initialize adjacency list
        for i in range(len(nodes)):
            self.adjList[i] = []

        self.obstacles = obstacles

        # count fixed nodes
        self.noFixedNodes = len(nodes) + len(self.getAllObstacleNodes())

        # numberToNode (BiMap equivalent)
        self.numberToNode = {}
        self.nodeToNumber = {}

        for i, node in enumerate(nodes):
            self.numberToNode[i] = node
            self.nodeToNumber[node] = i

        # Steiner nodes list
        self.steinerPoints = []

        # shortest paths storage
        if self.shortestPaths is None:
            self.shortestPaths = self.SPMap()

    # secondary constructor (clone-style)
    @classmethod
    def cloneConstructor(cls, nodes, obstacles, makeCopy):
        assert obstacles is not None, "Obstacle list can't be null."
        g = cls.__new__(cls)
        g.nodes = nodes
        g.obstacles = obstacles
        g.noFixedNodes = len(nodes) + len(g.getAllObstacleNodes())
        return g


    def resetSPstorage(self):
        self.shortestPaths = self.SPMap()

    def getNodeObject(self, i):
        return self.numberToNode.get(i)

    def getIndex(self, nod):
        assert nod in self.nodeToNumber, "This node does not exist."
        return self.nodeToNumber[nod]

    def nextFreeIndex(self, node):
        #node is the node that gets the index, returns next available indx
        assert not isinstance(node, LoadNode), "LoadNodes should not be added nor removed."

        if isinstance(node, SteinerNode):
            free = self.noFixedNodes
        else:
            free = len(self.nodes)

        while free in self.numberToNode:
            free += 1

        assert free not in self.adjList, "BiMap and adjList do not match!"
        assert isinstance(node, SteinerNode) or free < self.noFixedNodes, \
            "Obstacles should be stored within the fixed nodes range."

        return free

    def getDegree(self, node_or_index): #get degree of node based on adjacency list
        if isinstance(node_or_index, int): #if input is index
            idx = node_or_index
        else:
            idx = self.getIndex(node_or_index) #if input in node object
        return len(self.adjList[idx])

    def getAllEdges(self):
        edges = [] 
        #add all edges that are in order
        for i in self.adjList:
            for j in self.adjList[i]:
                if i < j:
                    edges.append((i, j))
        return edges

    def getNumberToNode(self):
        return self.numberToNode

    def numberEdges(self): #add up all degrees in graph then divide by 2 to get number of edges
        nr = 0
        for entry in self.adjList.values():
            nr += len(entry)
        return nr // 2

    def getLongestEdge(self, considerObstacles):
        longestEdge = (-1, -1) #will return this if there are no edges
        edges = self.getAllEdges()
        maxLength = -1.0

        for edge in edges:
            n1 = self.getNodeObject(edge[0])
            n2 = self.getNodeObject(edge[1])

            if considerObstacles:
                edgeLength = self.directDistance(n1, n2)
            else:
                edgeLength = n1.distanceTo(n2)

            if edgeLength > maxLength:
                maxLength = edgeLength
                longestEdge = edge #compare each edge until found the longest

        return longestEdge

    def getLoadNodes(self):
        return self.nodes

    def getSteinerNodes(self):
        return self.steinerPoints

    def getIncludedObstacleNodes(self):
        obstnodes = []
        for node in self.numberToNode.values():
            if self.isPartOfObstacles(node):
                obstnodes.append(node)  # assumed ObNode
        return obstnodes

    def getAllObstacleNodes(self):
        obstnodes = set()
        for obst in self.obstacles:
            for onode in obst.getPoints():
                obstnodes.add(onode)
        return obstnodes
    

    def getAllNodes(self):
        """
        Returns list of all nodes currently used in the graph
        (including obstacle nodes that are used)
        """
        return list(self.numberToNode.values())


    def getAllNodesAsArray(self):
        """
        Returns all nodes (Python doesn't distinguish list/array much)
        """
        return self.getAllNodes()


    def getObstacles(self):
        return self.obstacles


    def getNumberObstacles(self):
        return len(self.obstacles)


    def hasObstacles(self):
        return len(self.obstacles) > 0


    def isNodeInGraph(self, node):
        return node in self.numberToNode.values()


    def numberAllNodes(self):
        nr = len(self.adjList)
        assert nr == len(self.numberToNode), \
            "There was something wrong with the number of nodes."
        return nr


    def isLeafNode(self, thisNode):
        return self.getDegree(thisNode) == 1 #returns true if thisNode is a leaf


    # ---------- STEINER NODE MANAGEMENT ----------

    def addSteinerNodeFull(self, steiner, neighb1, neighb2, neighb3):
        neigh1ind = self.getIndex(neighb1)
        neigh2ind = self.getIndex(neighb2)
        neigh3ind = self.getIndex(neighb3)
    
        if steiner not in self.steinerPoints:
            self.steinerPoints.append(steiner)

            index = self.nextFreeIndex(steiner)
            print(f'add steiner node full, Steiner index = {index}')

            assert index not in self.numberToNode, \
                "There was a Steiner point at this place!"

            self.numberToNode[index] = steiner
            self.nodeToNumber[steiner] = index

            assert index not in self.adjList, \
                "The index was not free?"

            self.adjList[index] = []
            
            self.addEdge(index, neigh1ind)
            self.addEdge(index, neigh2ind)
            self.addEdge(index, neigh3ind)

            return index
        else:
            raise Exception("SteinerNode already exists")


    def addSteinerNode(self, steiner):
        if steiner not in self.steinerPoints:
            self.steinerPoints.append(steiner)

            index = self.nextFreeIndex(steiner)
            print(f'add steiner node, next free index for Steiner = {index}')

            assert index not in self.numberToNode, \
                "There was a Steiner point at this place!"

            self.numberToNode[index] = steiner
            self.nodeToNumber[steiner] = index

            if index not in self.adjList:
                self.adjList[index] = []
            else:
                raise Exception("Something went wrong")

            return index
        else:
            raise Exception("SteinerNode already exists")


    def removeSteinerNode(self, steiner):
        #removes Steiner Node from graph and all its edges
        i = self.getIndex(steiner)

        assert i in self.adjList, \
            "This SteinerNode does not exist"

        # remove edges
        for j in list(self.adjList[i]):
            self.adjList[j].remove(i) #removed the edges without changing the adjacency list yet

        # remove node
        del self.adjList[i] #remvoe steiner node from adj list
        self.steinerPoints.remove(steiner) #removing it from steiner points list

        removed = self.numberToNode.pop(i, None) #removing it from lookup
        self.nodeToNumber.pop(steiner, None)

        assert removed is not None, \
            "The Steiner node was not in there."


    def removeAllSteiners(self):
        #remove all Steiners and all incident edges
        count = 0
        while self.steinerPoints:
            stein = self.steinerPoints.pop(0)
            self.removeSteinerNode(stein)
            count += 1
        return count #returns number of Steiner points that got cleared


    # ---------- POSITION OPTIMISATION ----------

    def fineTuneSteinerPositions(self):
        #recalculates the posiiton of all Steiner points of degree 3
        #stops when positions do not change anymore 
        diff = 1.0

        while diff > 1e-5:
            diff = 0.0

            for stein in self.steinerPoints:
                if self.getDegree(stein) == 3:
                    i = self.getIndex(stein)

                    ne1 = self.getNodeObject(self.adjList[i][0])
                    ne2 = self.getNodeObject(self.adjList[i][1])
                    ne3 = self.getNodeObject(self.adjList[i][2])

                    position = self.SteinerLocation(ne1, ne2, ne3)

                    diffPos = max(
                        abs(position[0] - stein.getX()),
                        abs(position[1] - stein.getY())
                    )

                    diff = max(diffPos, diff)

                    stein.setNewLocation(position[0], position[1])


    # ---------- CLEANUP ----------
    def checkOrClearThis(self, stein):
        gotSomething = False
        degree = self.getDegree(stein)

        if degree == 3:
            return gotSomething #if deg = 3 no issue, return False

        if degree == 0 or degree > 3: #if degree of Steiner point is wrong
            print(f"WARNING: Steiner point with degree {degree}")
            raise Exception("This Steiner point is wrong somehow")

        elif degree == 1: #if deg = 1 remove that point
            self.removeSteinerNode(stein)
            gotSomething = True

        elif degree == 2: #if deg = 2, connect 2 nodes that are adjacent then remove steiner point
            steinInd = self.getIndex(stein)
            first = self.adjList[steinInd][0]
            second = self.adjList[steinInd][-1]

            if self.hasObstacles():
                self.addPath(self.getNodeObject(first),
                            self.getNodeObject(second))
            else:
                self.addEdge(first, second)

            self.removeSteinerNode(stein)
            gotSomething = True

        return gotSomething


    # ---------- OBSTACLE CHECKS ----------
    def isPartOfObstacles(self, onode):
        """
        True iff onode is a node in one of the obstacles (edge node)
        """
        if not isinstance(onode, ObNode):
            return False

        for obst in self.obstacles:
            if obst.containsCornerNode(onode):
                return True
        return False


    def isInsideOfObstacles(self, onode):
        """
        Returns the obstacle if node lies inside one (not on edge), else None
        """
        for obst in self.obstacles:
            if obst.containsNode(onode):
                return obst
        return None


    # ---------- OBSTACLE NODE MANAGEMENT ----------

    def addObstacleNode(self, onode):
        assert self.isPartOfObstacles(onode), \
            "You cannot add an obstacle node that is not part of any obstacle."

        index = self.nextFreeIndex(onode)
        print(f'add obs node, Ob node next free index = {index}')

        assert index not in self.numberToNode, \
            "There was already something there!"

        self.numberToNode[index] = onode
        self.nodeToNumber[onode] = index

        if index not in self.adjList:
            self.adjList[index] = []
        else:
            raise Exception("Something went wrong")

        return index


    def removeObstacleNode(self, onode):
        #print('removing ob node')
        assert self.isPartOfObstacles(onode), \
            "You cannot remove an obstacle node that is not part of any obstacle."

        i = self.getIndex(onode)

        assert i in self.adjList, \
            "This obstacleNode does not exist in the graph"

        # remove edges without changing adjacency list yet
        for j in list(self.adjList[i]):
            self.adjList[j].remove(i)

        # remove the obstacle node itself
        del self.adjList[i]

        #removing from lookup
        removed = self.numberToNode.pop(i, None)
        self.nodeToNumber.pop(onode, None)

        assert removed is not None, \
            "The node was not in there."


    def removeAllObstacleNodes(self):
        #remove all obstacle nodes from the graph
        obNodes = [node for node in self.getAllNodes()
                if self.isPartOfObstacles(node)] #add nodes from ALL nodes only if they are obstacle nodes

        count = 0
        for onode in obNodes:
            self.removeObstacleNode(onode)
            count += 1

        return count #returns number of obstacle nodes removed


    # ---------- EDGE MANAGEMENT ----------

    def addEdge(self, i, j):
        #from i to j (indices)
        #first check if nodes are the same
        assert i != j, "This graph cannot contain self-loops!"

        #second check are the nodes part of the graph
        assert i in self.adjList and j in self.adjList, \
            "You cannot add an edge to non-existent nodes"
        assert i in self.numberToNode and j in self.numberToNode, \
            "You cannot add an edge to non-existent nodes"

        #third check does the edge already exist
        assert j not in self.adjList[i] and i not in self.adjList[j], \
            "This edge already exists!"

        #if pass all checks then add to adj list
        self.adjList[i].append(j)
        self.adjList[j].append(i)


    def addEdgeByNode(self, nodei, nodej):
        #add edge from i to j (using nodes)
        iInGraph = self.isNodeInGraph(nodei)
        jInGraph = self.isNodeInGraph(nodej)

        assert iInGraph or self.isPartOfObstacles(nodei), \
            "Node i is not part of anything."
        assert jInGraph or self.isPartOfObstacles(nodej), \
            "Node j is not part of anything."

        if not iInGraph:
            self.addObstacleNode(nodei)
        if not jInGraph:
            self.addObstacleNode(nodej)

        indexi = self.getIndex(nodei)
        indexj = self.getIndex(nodej)

        self.addEdge(indexi, indexj)


    # ---------- PATH ADDITION ----------

    def addPath(self, start, end):
        pl = self.astarWithObstacles(start, end)
        path = pl.getPath()

        for n in range(1, len(path)):
            if n < len(path) - 1 and not self.isNodeInGraph(path[n]):
                assert isinstance(path[n], ObNode), \
                    "Path contains non-obstacle nodes not in graph"

                self.addObstacleNode(path[n])

            self.addEdgeByNode(path[n - 1], path[n])


    # ---------- EDGE CHECKS ----------

    def doesEdgeExist(self, i, j):
        if i not in self.adjList or j not in self.adjList:
            return False

        a = j in self.adjList[i]
        assert a == (i in self.adjList[j]), \
            "Graph inconsistency detected"

        return a #returns true if edge already in graph


    def removeEdge(self, i, j):
        #i, j indices of nodes
        assert self.doesEdgeExist(i, j), \
            "This edge does not seem to exist"

        self.adjList[i].remove(j)

        assert i in self.adjList[j], \
            "This edge does not seem to exist"

        self.adjList[j].remove(i)


    def removeAllEdges(self):
        for entry in self.adjList.values():
            entry.clear()


    def removeEdgesInPart(self, indices):
        #remove edges that connect to at least one node from the list of indices
        count = 0
        edges = self.getAllEdges()

        for (u, v) in edges:
            if u in indices or v in indices:
                self.removeEdge(u, v)
                count += 1

        return count #return number of edges removed


    # ---------- EDGE REMOVE + RECONNECT ----------

    def removeEdgeAndReconnect(self, i, j, withObstacles):
        #if withObstacles is true it will remove if an obstacle becomes of degree 1
        if withObstacles:
            self.removeReconnectOb(i, j) 
        else:
            self.removeReconnect(i, j)


    def removeReconnect(self, i, j):
        #removed edge from node i and j
        #If one of the adjacent nodes was a Steiner point, remove this point and reconnect the other two nodes

        #remove edge
        self.removeEdge(i, j)

        nod1 = self.getNodeObject(i)
        nod2 = self.getNodeObject(j)

        for stein in [nod1, nod2]:
            if isinstance(stein, SteinerNode): #if edge includes a steiner node
                #remove it and reconnect other adjacent nodes

                otherTwo = self.adjList[self.getIndex(stein)]

                assert len(otherTwo) == 2, \
                    f"Steiner node degree issue: {len(otherTwo)}"

                first = otherTwo[0]
                second = otherTwo[-1]

                self.addEdge(first, second) #add new edge

                self.removeSteinerNode(stein) #remove steiner point and updates neighbours

    # -------------------------------
    # removeReconnect_ob
    # -------------------------------
    def removeReconnectOb(self, i, j):
        self.removeEdge(i, j) #remove edge using node indices

        nod1 = self.getNodeObject(i)
        nod2 = self.getNodeObject(j)
        edge_nodes = [nod1, nod2]

        # --- Handle Steiner nodes ---
        # if the edge includes a steiner node then remove the node and reconnect adjacent nodes
        for stein in edge_nodes:
            if isinstance(stein, SteinerNode): #if this is a SteinerNode, remove it and reconnect the other two nodes!
                stein_index = self.getIndex(stein)
                other_two = self.adjList[stein_index]

                assert len(other_two) == 2, (
                    "Something went wrong in remove_reconnect_ob. "
                    f"Degree = {len(other_two)}. This Steiner does not have two adjacent nodes"
                )

                first = self.getNodeObject(other_two[0])
                second = self.getNodeObject(other_two[1])

                #reconnect adjacent nodes
                print(f'remove reconnect ob, add path between {self.getIndex(first)}, {self.getIndex(second)}')
                print(f'remove reconnect ob, current adj list: {self.adjList}')
                self.addPath(first, second)
                #remove steiner
                self.removeSteinerNode(stein)

        # --- Handle obstacle nodes ---
        for obn in edge_nodes:
            if isinstance(obn, ObNode) and self.getDegree(obn) == 1:
                obn_index = self.getIndex(obn)
                other = self.adjList[obn_index][0]

                self.removeReconnectOb(other, obn_index)
                self.removeObstacleNode(obn)


    # -------------------------------
    # displayGraphMap: displays the adjacency list
    # -------------------------------
    def displayGraphMap(self):
        for key, value in self.adjList.items():
            print(f"{key} --> {value}")


    # -------------------------------
    # MSTparts (wrapper)
    # performs a prims MST on this part of the tree
    # -------------------------------
    def MSTParts(self, thispart, consider_obstacle_cost=False):
        # Get indices of 'thispart'
        indices = []
        for nod in thispart:
            assert nod in self.numberToNode.values(), \
                "Node not part of graph"
            indices.append(self.getIndex(nod))

        n = len(thispart)
        assert n == len(indices)

        # Remove all edges in this part
        self.removeEdgesInPart(indices)

        total_dist = 0.0

        #this si the MST algorithm
        # msts[i] = [node_index, current_distance, predecessor]
        msts = [[idx, float("inf"), indices[0]] for idx in indices]
        #array should have the following form
        # [node index/number, current distance squared, predecessor index]
        # where current distance is initialised as inf

        for j in range(1, n):
            min_dist = float("inf") #reset min dist to a larger number
            min_i = j

            l = msts[j - 1][0] #getting the node index

            for i in range(j, n):
                k = msts[i][0] #gettting the node number

                if consider_obstacle_cost: #if we are considering obstacts
                    dist_new = self.directDistance( #use the distacne with obstacles
                        self.getNodeObject(k),
                        self.getNodeObject(l)
                    )
                else:
                    dist_new = self.getNodeObject(k).distanceSqrTo(
                        self.getNodeObject(l) #else use squared distance
                    )

                if dist_new < msts[i][1]: #if distance is better
                    msts[i][1] = dist_new #update to new distance
                    msts[i][2] = l #update new node index

                if msts[i][1] < min_dist: #if not better then leave as is
                    min_dist = msts[i][1] 
                    min_i = i

            # Swap
            msts[j], msts[min_i] = msts[min_i], msts[j]

            # Add edge
            self.addEdge(msts[j][0], msts[j][2])

            if consider_obstacle_cost:
                total_dist += min_dist
            else:
                total_dist += math.sqrt(min_dist)

        return total_dist


    # -------------------------------
    # MSTwithObstacles: Prims MST alg while moving around obstacles
    # -------------------------------
    def MSTWithObstacles(self, thispart): #this part is the array of terminals
        total = 0.0

        #save the indices
        indices = []
        for nod in thispart:
            assert nod in self.numberToNode.values(), \
                "Node not part of graph"
            indices.append(self.getIndex(nod))

        n = len(thispart)
        assert n == len(indices)

        self.removeEdgesInPart(indices) #remove all edges in 'thispart'

        # this array has the following format
        # [node number, current distance, predecessor index]
        msts = [[idx, float("inf"), indices[0]] for idx in indices]

        extra_nodes_added = False

        j = 1
        while j < len(msts): #the size of msts will change
            print(f'MSTs = {msts}')
            min_dist = float("inf") #reset min dist to large number
            min_i = j

            startL = self.getNodeObject(msts[j - 1][0]) #get starting node 
            

            for i in range(j, len(msts)):
                endK = self.getNodeObject(msts[i][0]) #get nodes
                pl = self.astarWithObstacles(startL, endK) #shortest path length considering obstacles 

                dist_new = pl.getValue() #length of path (without considering obstacels)

                if dist_new < msts[i][1]:
                    msts[i][1] = dist_new # update to new shortest dist
                    msts[i][2] = msts[j - 1][0] # update node

                if msts[i][1] < min_dist: #if not shorter
                    min_dist = msts[i][1]
                    min_i = i

            start = self.getNodeObject(msts[min_i][2]) #predecessor of closest node
            end = self.getNodeObject(msts[min_i][0]) #closest node to be added

            pl = self.astarWithObstacles(start, end) #shortest path with obstacles
            path = pl.getPath()
            dist_values = pl.getValues()

            next_j = j

            # Insert intermediate nodes
            for n_idx in range(1, len(path) - 1):
                node = path[n_idx]

                if not self.isNodeInGraph(node): #check if node is in path
                    assert isinstance(node, ObNode)
                    self.addObstacleNode(node)
                    print('add ob node')

                msts.insert(next_j, [ #update msts array
                    self.getIndex(node),
                    dist_values[n_idx],
                    self.getIndex(path[n_idx - 1])
                ])

                next_j += 1
                min_i += 1
                extra_nodes_added = True

            # Update final node
            # setting predecessor and distance for actual node
            msts[min_i][1] = dist_values[-1]
            msts[min_i][2] = self.getIndex(path[-2])

            # Swap
            msts[next_j], msts[min_i] = msts[min_i], msts[next_j]

            j += 1

        # If we added nodes → rerun MST over all nodes
        if extra_nodes_added:
            all_nodes = [
                self.getNodeObject(msts[i][0]) for i in range(len(msts))
            ]
            return self.MSTParts(all_nodes, True)

        # Otherwise add edges
        for i in range(1, len(msts)):
            a = msts[i][0]
            b = msts[i][2]
            total += msts[i][1]
            self.addEdge(a, b)

        return total
    
    # calculates distance between nodes including obstacle crossing costs
    # if a solid obstacle is crossed then it returns MAX_VALUE
    def directDistance(self, node1, node2):
        #assert node1 is not node2, "directDist nodes are the same"
        if node1 is node2: return 0.0

        normal_dist = node1.distanceTo(node2)
        if not self.hasObstacles(): #if no obstacle crossings   
            return normal_dist

        crossing_costs = normal_dist
        #print("number of obstacles: ", len(self.obstacles))
        i=0
        for obst in self.obstacles:
            line_cross = obst.calculateLineCrossDist(node1, node2) #calc the intersecting distance            i+=1
            if line_cross > 0.0 and obst.isSolid(): #if crossing a solid object
                return float("inf")
            if line_cross > 0.0:
                crossing_costs += line_cross * (obst.getCrossCosts() - 1.0) #add in crossing costs
        #if math.isnan(crossing_costs):
        #    return float("inf")
    
        return crossing_costs
    
    #calc dijsktras shortest path alg while avoiding obstacles
    def dijkstraWithObstacles(self, start, end):
        with_obstacles = self.hasObstacles()
        are_loads = isinstance(start, LoadNode) and isinstance(end, LoadNode)

        if not are_loads:
            self.nonloads += 1

        # Check cache, checks is shortest distance has been calculated already
        sp = self.shortestPaths.get(start, end) #might be in reverse order
        if are_loads and sp is not None:
            return sp #if already calculated return shortest path

        value = start.distanceTo(end)

        if (not with_obstacles or start == end or
            abs(value - self.directDistance(start, end)) <= Graph.TOLERANCE):

            pl = Graph.PathLength([start, end], [0.0, value])
            if are_loads:
                self.shortestPaths.put(start, end, pl)
            return pl

        value = 0

        # Build node list
        obstnodes = self.getAllObstacleNodes()
        considered_nodes = [start, end] + list(obstnodes)

        startindex = 0
        endindex = 1
        n = len(considered_nodes)

        # this is Dijkstra's Alg

        # seen: [node_index, distance]
        seen = [[i, float("inf")] for i in range(n)]

        # predecessor: [predecessor_index, distance_to_predecessor]
        predecessor = [[startindex, float("inf")] for _ in range(n)]

        seen[0][1] = 0.0
        predecessor[0][1] = 0.0

        for current in range(n - 1):
            min_dist = float("inf") #reset min dist to large number
            min_i = current + 1  #! this might be wrong -> different from source material

            for next_i in range(current + 1, n):
                nex = seen[next_i][0] #getting the node indices
                cur = seen[current][0]

                dist = seen[next_i][1]
                link_dist = self.direct_distance(
                    considered_nodes[cur],
                    considered_nodes[nex]
                )

                dist_new = seen[current][1] + link_dist

                if dist_new < dist:
                    seen[next_i][1] = dist_new
                    predecessor[nex][0] = cur
                    predecessor[nex][1] = link_dist
                    dist = dist_new

                if dist < min_dist:
                    min_dist = dist
                    min_i = next_i

            # swapping minimum distant node to next current position
            seen[current + 1], seen[min_i] = seen[min_i], seen[current + 1]

            if seen[current + 1][0] == endindex:
                break

        # Reconstruct path
        final_path_rev = [(endindex, predecessor[endindex][1])]
        index = endindex

        while index != startindex:
            index = predecessor[index][0] #update index to next in path
            final_path_rev.append((index, predecessor[index][1])) # update ndoe order

        final_path = []
        values = []

        for idx, val in reversed(final_path_rev):
            final_path.append(considered_nodes[idx])
            values.append(val)

        assert final_path[0] == start
        assert final_path[-1] == end

        pl = Graph.PathLength(final_path, values)

        if are_loads:
            self.shortestPaths.put(start, end, pl)

        return pl   
    
    #calc A* alg for the shortest path while avoiding/considering high cost obstacles
    #returns array of nodes in shortest path and the length of the path including obstacles
    '''def astarWithObstacles(self, start, end):
        #print("A star with obst")
        with_obstacles = self.hasObstacles()
        are_loads = isinstance(start, LoadNode) and isinstance(end, LoadNode)

        if not are_loads:
            self.nonloads += 1
            #print("non loads?")


        # Cache check
        sp = self.shortestPaths.get(start, end) #might be in reverse order
        if sp:
            val = sp.getValue()
        else: 
            val = sp
        print(f'in a star with obs sp cache value between {self.getIndex(start)} and {self.getIndex(end)} = {val}')
        if are_loads and sp is not None: #checks if shortest path has been calculated
            return sp

        value = start.distanceTo(end) #length of path without obstacles

        if (not with_obstacles or start == end or
            abs(value - self.directDistance(start, end)) <= Graph.TOLERANCE):

            sp = Graph.PathLength([start, end], [0.0, value])
            if are_loads:
                self.shortestPaths.put(start, end, sp) #add to storage
            return sp

        obstnodes = self.getAllObstacleNodes()
        considered_nodes = [start, end] + list(obstnodes)

        startindex = 0
        endindex = 1
        n = len(considered_nodes)
 
        #this is the A* algorithm
        # the number array has the following format
        # [node number, current distance, remaining estimate] = [node number, g, h]
        # node number and predecessor doe not refer to the index in the graph 
        # instead it is the index in consideredNodes only

        # seen: [node_index, g, h]
        seen = [[i, float("inf"), considered_nodes[i].distanceTo(end)]
                for i in range(n)]
        # predecessor: [prev_index, dist_to_prev]
        predecessor = [[startindex, float("inf")] for _ in range(n)]

        seen[0][1] = 0.0
        predecessor[0][1] = 0.0
        min_i = 0

        for current in range(n - 1): #going through seen array
            min_f = float("inf") #reset min dist to a large number
            #min_i = current + 1 #!need to check

            for next_i in range(current + 1, n):  #going through seen
                #getting the node numbers from 'consideredNodes'
                nex = seen[next_i][0]
                cur = seen[current][0]

                g = seen[next_i][1]
                h = seen[next_i][2]

                link_dist = self.directDistance(
                    considered_nodes[cur],
                    considered_nodes[nex]
                )

                g_new = seen[current][1] + link_dist

                if g_new < g: #update g with g_new
                    seen[next_i][1] = g_new # upsate current dist
                    predecessor[nex][0] = cur
                    predecessor[nex][1] = link_dist
                    g = g_new

                f = g + h

                if f < min_f:
                    min_f = f
                    min_i = next_i

            # swapping min distant node to next current position
            temp = seen[current + 1]
            seen[current + 1] = seen[min_i]
            seen[min_i] = temp

            if seen[current + 1][0] == endindex:
                break

        # Reconstruct path - make the node order
        final_path_rev = [(endindex, predecessor[endindex][1])]
        index = endindex

        while index != startindex:
            index = predecessor[index][0]
            # distnace between this index and predecessor (this index has changed - is the new index)
            final_path_rev.append((index, predecessor[index][1]))

        final_path = [] #array of nodes in path
        values = [] #array of numbers to represent the value of the path

        final_path_length = len(final_path_rev)
        final_path = [None] * final_path_length
        values = [0.0] * final_path_length

        for i in range(final_path_length - 1, -1, -1):
            rev = final_path_rev[i]
            final_path[final_path_length - 1 - i] = considered_nodes[int(rev[0])]
            values[final_path_length - 1 - i] = float(rev[1])

        assert final_path[0] == start
        assert final_path[-1] == end

        sp = Graph.PathLength(final_path, values) #creating the PathLength object

        if are_loads:
            self.shortestPaths.put(start, end, sp) #adding to storage
        
        print(f'in a star with obs sp output value between {self.getIndex(start)} and {self.getIndex(end)} = {sp.getValue()}')

        return sp'''
    

    #start = node object, end = node object, astarwithobstacles outputs a pathlength object
    def astarWithObstacles(self, start, end):
        with_obstacles = self.hasObstacles()
        are_loads = isinstance(start, LoadNode) and isinstance(end, LoadNode)

        if not are_loads:
            self.nonloads += 1

        sp = self.shortestPaths.get(start, end)
        if sp:
            val = sp.getValue()
        else: 
            val = sp
        print(f'in a star with obs sp cache value between {self.getIndex(start)} and {self.getIndex(end)} = {val}')
        if are_loads and sp is not None:
            return sp

        value = start.distanceTo(end)
        if (not with_obstacles or start == end or
                abs(value - self.directDistance(start, end)) <= Graph.TOLERANCE):
            sp = Graph.PathLength([start, end], [0.0, value])
            if are_loads:
                self.shortestPaths.put(start, end, sp)
            return sp

        start_index = 0
        end_index = 1

        # Get all obstacle nodes
        obst_nodes = self.getAllObstacleNodes()

        considered_nodes = [None] * (len(obst_nodes) + 2)
        considered_nodes[0] = start
        considered_nodes[1] = end
        laenge = 2
        for nod in obst_nodes:
            considered_nodes[laenge] = nod
            laenge += 1

        # A* algorithm
        # seen entries: [node_number, g (current distance), h (heuristic estimate)]
        # predecessor entries: [predecessor_node_number, distance_to_predecessor]
        seen = [[i, float('inf'), considered_nodes[i].distanceTo(end)] for i in range(laenge)]
        predecessor = [[start_index, float('inf')] for _ in range(laenge)]

        seen[0][1] = 0.0
        predecessor[0][1] = 0.0

        min_i = 0
        for current in range(laenge - 1):
            min_f = float('inf')
            for next_ in range(current + 1, laenge):
                nex = seen[next_][0]
                cur = seen[current][0]

                g = seen[next_][1]
                h = seen[next_][2]
                link_dist = self.directDistance(considered_nodes[cur], considered_nodes[nex])
                g_new = seen[current][1] + link_dist

                if g_new < g:
                    seen[next_][1] = g_new
                    predecessor[seen[next_][0]][0] = seen[current][0]
                    predecessor[seen[next_][0]][1] = link_dist
                    g = g_new

                f = g + h
                if f < min_f:
                    min_i = next_
                    min_f = f

            # Swap minimum node to next current position
            seen[current + 1], seen[min_i] = seen[min_i], seen[current + 1]

            if seen[current + 1][0] == end_index:
                break

        # Reconstruct path in reverse
        final_path_reverse = [[end_index, predecessor[end_index][1]]]
        index = end_index
        while index != start_index:
            index = predecessor[index][0]
            final_path_reverse.append([index, predecessor[index][1]])

        # Reverse into correct order
        final_path_length = len(final_path_reverse)
        final_path = [None] * final_path_length
        values = [0.0] * final_path_length
        for i in range(final_path_length - 1, -1, -1):
            rev = final_path_reverse[i]
            final_path[final_path_length - 1 - i] = considered_nodes[int(rev[0])]
            values[final_path_length - 1 - i] = float(rev[1])

        assert final_path[0] == start, "Something with the path start is incorrect"
        assert final_path[-1] == end, "Something with the path end is incorrect"

        sp = Graph.PathLength(final_path, values)
        if are_loads:
            self.shortestPaths.put(start, end, sp)
        print(f'in a star with obs sp output value between {self.getIndex(start)} and {self.getIndex(end)} = {sp.getValue()}')

        return sp
    # -------------------------------
    # getConnComponents
    # -------------------------------
    def getConnComponents(self):
        partition = []

        # basis = all node indices including Steiner points
        basis = list(self.adjList.keys())

        while len(basis) > 0:
            part = []
            
            # start with one unvisited node
            start = basis[0]
            part.append(start)

            new_add = [start]

            # BFS-like expansion
            while len(new_add) > 0:
                new_new_add = []

                for i in new_add:
                    for j in self.adjList[i]:
                        if j not in part:
                            part.append(j)
                            new_new_add.append(j)

                new_add = new_new_add

            # remove all nodes in this component from basis
            for k in part:
                if k in basis:
                    basis.remove(k)
            #addd connected component to the partition
            partition.append(part)

        return partition


    # -------------------------------
    # nrConnComponents: integer representing the number of connected components in the graph
    # -------------------------------
    def nrConnComponents(self):
        return len(self.getConnComponents())

    #calculates the angle at the middle node between the two edges
    #returns 2 elements, first = quadrant referring to base as the base line
    # second = tangens
    def quadrantAndTan(self, middle, base, a):
        xbase = base.x - middle.x
        ybase = base.y - middle.y
        xa = a.x - middle.x
        ya = a.y - middle.y

        cross = xbase * ya - xa * ybase #cross produce
        dot = xbase * xa + ybase * ya #dot product

        tan = cross / dot if dot != 0 else float("inf") 

        if dot >= 0:
            if cross >= 0:
                quadrant = 1  # upper right
            else:
                quadrant = 4  # lower right
        else:
            if cross >= 0:
                quadrant = 2  # upper left
            else:
                quadrant = 3  # lower left

        return quadrant, tan
    

    def angleSmall(self, middle, b, a):
        #reutns true if the angle connecting middle node to nodes a and b are less than 120
        quadrant, tan = self.quadrantAndTan(middle, b, a)

        if quadrant in (1, 4):
            return True

        if quadrant == 2:
            if tan < Graph.TAN120 - Graph.TOLERANCE:
                return True
        else:
            assert quadrant == 3
            if tan > -Graph.TAN120 + Graph.TOLERANCE:
                return True

        return False
    
    def angleBig(self,middle, b, a):
        #reutns true if the angle between nodes middle, a and b are more than 120
        quadrant, tan = self.quadrantAndTan(middle, b, a)

        if quadrant in (1, 4):
            return False

        if quadrant == 2:
            if tan > Graph.TAN120 + Graph.TOLERANCE: #angle inclusing tolerance
                return True
        else:
            assert quadrant == 3
            if tan < -Graph.TAN120 - Graph.TOLERANCE:
                return True

        return False
    
    #comparing two different angles at one given node
    #reutrn true if angle between baseA and A is smaller than the angle between baseB and B
    def smallerAngle(self, middle, baseA, a, baseB, b):
        quadrantA, tanA = self.quadrantAndTan(middle, baseA, a)
        quadrantB, tanB = self.quadrantAndTan(middle, baseB, b)

        if quadrantA != quadrantB:
            return quadrantA < quadrantB

        return tanA < tanB
    

    #gets a list of all adjacent angles of the form {[middle, node1, node2 ], [middle, node2, node3], ... }
    def anglesAtNode(self, middle):
        #returns list of arrays that represent agles
        #followed by other adjacent nodes in anti clockwise manner
        angles = []

        degree = self.getDegree(middle)
        print(f'node {self.getIndex(middle)} has degree {degree}')
        if degree <= 1:
            return angles #there is no angle

        #degree is at least 2
        middle_index = self.getIndex(middle)
        neighbors = self.adjList[middle_index]

        base = self.getNodeObject(neighbors[0]) #first
        first = self.getNodeObject(neighbors[1]) #second
        print(f'node {self.getIndex(middle)} has neighbours {neighbors}: base = {base}, first = {first}')

        # Degree 2 case
        if degree == 2:
            if self.smallerAngle(middle, base, first, first, base):
                angles.append([middle, base, first])
            else:
                angles.append([middle, first, base])
            return angles

        # Degree >= 3
        # sorting
        ordered = [base, first]

        for i in range(2, degree):
            a = self.getNodeObject(neighbors[i])
            a_index = i

            while a_index > 1:
                b = ordered[a_index - 1]
                if self.smallerAngle(middle, base, a, base, b):
                    a_index -= 1
                else:
                    break

            ordered.insert(a_index, a)

        # Create angles - adding all angles
        for j in range(1, degree):
            angles.append([middle, ordered[j - 1], ordered[j]])

        # Closing angle - adding last angle
        angles.append([middle, ordered[-1], ordered[0]])

        return angles
    

    #returns true if the given node has at least 2 neighbours and at least one angle of less than 120 degrees
    def hasSmallAngle(self, this_node): #this_node is index of node
        assert this_node in self.adjList and this_node in self.numberToNode

        degree = self.getDegree(this_node)

        if degree > 3:
            return True #this means there

        if degree < 2:
            return False #this means degree one in a MST

        #if degree is 2 or 3
        neighbors = self.adjList[this_node]

        neigh1 = self.getNodeObject(neighbors[0])
        neigh2 = self.getNodeObject(neighbors[1])
        middle = self.getNodeObject(this_node)

        angle1_small = self.angleSmall(middle, neigh1, neigh2)

        #in the case of rounding errors allow for tolerance
        #in the case of degree 2
        if degree == 2:
            return angle1_small

        #in the case of degree 3
        if angle1_small:
            return True

        #if angle1 was greater/equal 120 then check angle2
        neigh3 = self.getNodeObject(neighbors[2])

        if self.angleSmall(middle, neigh1, neigh3):
            return True

        if self.angleSmall(middle, neigh2, neigh3):
            return True

        return False
    

    #returns list of all nodes of degree 2 or higher with angles less than 120 (potentially steiner points and obstacle nodes)
    def getAllNodesWithSmallAngles(self, with_steiner):
        these_nodes = []

        for nod in self.numberToNode.keys():
            node_obj = self.getNodeObject(nod)

            if with_steiner:
                if self.hasSmallAngle(nod):
                    these_nodes.append(nod)
            else:
                if not isinstance(node_obj, SteinerNode) and self.hasSmallAngle(nod):
                    these_nodes.append(nod)

        return these_nodes
    
    #returns list of all load nodes(terminals) with angle of less than 120
    #nodes of degree 2 or higher
    def getNodesWithSmallAnglesIn(self, thispart):
        these_nodes = []

        for node in thispart:
            nod = self.getIndex(node)
            if self.hasSmallAngle(nod):
                these_nodes.append(nod)

        return these_nodes
    

    #returns array with 2 entries, x coord and y coord
    #Calculates the coordinates of the Fermat-Toricelli Point given its three connected points
    def SteinerLocation(self, A, B, C):
        a_sq = B.distanceSqrTo(C)
        b_sq = A.distanceSqrTo(C)
        c_sq = A.distanceSqrTo(B)

        a = math.sqrt(a_sq)
        b = math.sqrt(b_sq)
        c = math.sqrt(c_sq)

        if (a == 0) or (b == 0) or (c == 0): print(f'Steiner location division by zero coming: {a}, {b}, {c}')

        angleA = math.acos((b_sq + c_sq - a_sq) / (2.0 * b * c))
        angleB = math.acos((a_sq + c_sq - b_sq) / (2.0 * a * c))
        angleC = math.acos((a_sq + b_sq - c_sq) / (2.0 * a * b))

        triX = 1.0 / math.sin(angleA + math.pi / 3.0)
        triY = 1.0 / math.sin(angleB + math.pi / 3.0)
        triZ = 1.0 / math.sin(angleC + math.pi / 3.0)

        denom = a * triX + b * triY + c * triZ

        x = ((a * triX) / denom) * A.x + ((b * triY) / denom) * B.x + ((c * triZ) / denom) * C.x
        y = ((a * triX) / denom) * A.y + ((b * triY) / denom) * B.y + ((c * triZ) / denom) * C.y

        return [x, y]
    

    #find out the 2 connecting nodes that build the smallest angle at this node
    def findSmallestAngle(self, middleind):
        degree = self.getDegree(middleind)
        assert degree >= 2

        middle = self.getNodeObject(middleind)
        angles = self.anglesAtNode(middle)
        print(f'smallest angle at {middleind}, ({middle.get_x()}, {middle.get_y()}) is: {angles}')

        neigh1_base, neigh2 = angles[0][1], angles[0][2]

        if degree != 2:
            quadrant, tan = self.quadrantAndTan(middle, neigh1_base, neigh2)

            for angle in angles:
                quad, ta = self.quadrantAndTan(middle, angle[1], angle[2])

                if (quad < quadrant) or (quad == quadrant and ta < tan):
                    neigh1_base = angle[1]
                    neigh2 = angle[2]
                    quadrant = quad
                    tan = ta

        return [neigh1_base, neigh2]
    


    #Inserting a SteinerPoint at the node neigh1ind: the smallest angle is chosen.
	# No obstacles are considered!
	# (uncomment section in findSmallestAngle() if any angle would be sufficient) 
	# 3 Options: 
	# option 1: new Steiner node was inserted --> return new Steiner node
    # option 2: Steiner node was 'moved' to corrected position --> return Steiner node
    # option 3: Steiner node removed and neighbouring nodes were rewired --> return corner node
    # option 4: nothing was changed --> return null
    def insertSteinerHere(self, middleind, with_obstacle):
        #middleind = index of where steiner node should be added
        assert self.hasSmallAngle(middleind)

        if with_obstacle and self.hasObstacles(): # if we consider obstacles 
            return self.ishObstacles(middleind)

        # if no obstacles 
        middle = self.getNodeObject(middleind)
        option = 1

        neighbors = self.adjList[middleind]
        degree = len(neighbors)

        #find the 2 connecting nodes that build the small angle
        #set initial values
        neigh2ind = neighbors[0]
        neigh3ind = neighbors[-1]
        neigh2 = self.getNodeObject(neigh2ind)
        neigh3 = self.getNodeObject(neigh3ind)

        got_removed = False #turns true if nigh1 was a Steiner Node and got replaced

        # Steiner node removal case
        #if degree == 3 and Steiner node then remove neigh1 and replace it
        #edges already got removed so set got_removed to true
        if isinstance(middle, SteinerNode) and degree == 3:
            option = 2
            #copying neighbours
            neighbs = [self.getNodeObject(n) for n in neighbors]

            self.removeSteinerNode(middle) #here removes all edges as well
            got_removed = True #remember the node was removed

            #check if we need to re-wire or still inster a new Steiner point
            longest = 0
            corner = 0

            for k in range(3):
                edge = neighbs[(k+1)%3].distanceSqrTo(neighbs[(k+2)%3]) #edge opposite of neighbs[k]
                if edge > longest:
                    longest = edge #if edge is longest then update longest edge
                    corner = k
            
            #replace neigh1
            middle = neighbs[corner]
            neigh2 = neighbs[(corner + 1) % 3]
            neigh3 = neighbs[(corner + 2) % 3]
            #no need to update neigh1ind, neigh2ind, neigh3ind as they do not get used if got_removed is true

            #if angle is not small then just reconnect and return null
            if self.angleBig(middle, neigh2, neigh3):
                option = 3
                self.addEdge(self.getIndex(middle), self.getIndex(neigh2))
                self.addEdge(self.getIndex(middle), self.getIndex(neigh3))
                return ResultPair(option, middle) #if rewired stop here

        elif degree >= 3:
            #find the two nodes building the smallest angle
            neigh2, neigh3 = self.findSmallestAngle(middleind)
            neigh2ind = self.getIndex(neigh2)
            neigh3ind = self.getIndex(neigh3)

        st_loc = self.SteinerLocation(middle, neigh2, neigh3)
        new_stein = SteinerNode(st_loc[0], st_loc[1])

        self.addSteinerNodeFull(new_stein, middle, neigh2, neigh3)
        #above includes adding new edges

        #deleting old edges if they have not been removed already
        if not got_removed:
            self.removeEdge(middleind, neigh2ind)
            self.removeEdge(middleind, neigh3ind)

        return ResultPair(option, new_stein)    
    


    # ------------------------------------------------------------
    # ishObstacles: helper method for insert_steiner_here()
    # ------------------------------------------------------------
    def ishObstacles(self, middleind):
        middle = self.getNodeObject(middleind)
        option = 4
        degree = self.getDegree(middleind) #degree of node

        # --------------------------------------------------------
        # CASE 1: middle is Steiner node with degree 3
        # remove neigh 1 and replace it
        # --------------------------------------------------------
        if isinstance(middle, SteinerNode) and degree == 3:

            old_stein = middle

            #copying neighbours
            neighbs = [self.getNodeObject(nei) for nei in self.adjList[middleind]]

            dist_original = sum(self.directDistance(old_stein, n) for n in neighbs)

            # check if we need to rewire or insert new steiner
            # find longest edge
            longest_edge = 0.0
            corner_k = 0 #corner opposite longest edge
            for k in range(3):
                edge = self.directDistance(
                    neighbs[(k + 1) % 3], neighbs[(k + 2) % 3]
                )
                if edge > longest_edge:
                    longest_edge = edge
                    corner_k = k

            #replace middle
            middle = neighbs[corner_k]
            neigh2 = neighbs[(corner_k + 1) % 3]
            neigh3 = neighbs[(corner_k + 2) % 3]

            dist_rewired = (
                self.directDistance(middle, neigh2)
                + self.directDistance(middle, neigh3)
            )

            #calc potential 'move of steiner point
            st_loc = self.SteinerLocation(middle, neigh2, neigh3)
            new_stein = SteinerNode(st_loc[0], st_loc[1])

            dist_new_stein = (
                self.directDistance(new_stein, middle)
                + self.directDistance(new_stein, neigh2)
                + self.directDistance(new_stein, neigh3)
            )

            if dist_new_stein < dist_original and self.angleSmall(middle, neigh2, neigh3):
                option = 2
                if dist_rewired < dist_new_stein:
                    option = 3
            elif dist_rewired < dist_original:
                option = 3

            if option == 4:
                return ResultPair(option, None)

            self.removeSteinerNode(old_stein) #here removes all edges

            if option == 3: #reconnect and return middle
                self.addEdge(middle, neigh2)
                self.addEdge(middle, neigh3)
                return ResultPair(option, middle) #if rewired stop here

            #if option = 2
            self.addSteinerNodeFull(new_stein, middle, neigh2, neigh3)
            return ResultPair(option, new_stein)

        # --------------------------------------------------------
        # CASE 2: normal node: find out the two connecting nodes that build the smallest angle
        # --------------------------------------------------------
        else:
            angles = self.anglesAtNode(middle)

            for sm_angle in angles:
                neigh2, neigh3 = sm_angle[1], sm_angle[2] #change to 0 and 1 if find_smallest_angle() used

                if not self.angleSmall(middle, neigh2, neigh3):#delete if find_smallest_angle() is used
                    continue 

                neigh2ind = self.getIndex(neigh2)
                neigh3ind = self.getIndex(neigh3)

                dist_original = (
                    self.directDistance(middle, neigh2)
                    + self.directDistance(middle, neigh3)
                )

                st_loc = self.SteinerLocation(middle, neigh2, neigh3)
                new_stein = SteinerNode(st_loc[0], st_loc[1])

                dist_new_stein = (
                    self.directDistance(new_stein, middle)
                    + self.directDistance(new_stein, neigh2)
                    + self.directDistance(new_stein, neigh3)
                )

                if dist_new_stein < dist_original:
                    option = 1
                    self.addSteinerNodeFull(new_stein, middle, neigh2, neigh3) #includes adding new edges

                    #remove old edges
                    self.removeEdge(middleind, neigh2ind)
                    self.removeEdge(middleind, neigh3ind)
                else:
                    option = 4 #not necessary
                    new_stein = None

                if option != 4:
                    return ResultPair(option, new_stein)

            return ResultPair(4, None)


    # ------------------------------------------------------------
    # insertForcedSteinerHere : use if MST cannot be guaranteed
    # doesn't rewire or remove false steiner points
    # ------------------------------------------------------------
    def insertForcedSteinerHere(self, neigh1ind, with_obstacle):
        assert self.hasSmallAngle(neigh1ind)

        neigh1 = self.getNodeObject(neigh1ind)

        [neigh2, neigh3] = self.findSmallestAngle(neigh1ind)
        

        neigh2ind = self.getIndex(neigh2)
        neigh3ind = self.getIndex(neigh3)
        print(f'smallest angle at node {neigh1ind} is with {neigh2ind} and {neigh3ind}')

        st_loc = self.SteinerLocation(neigh1, neigh2, neigh3)
        new_stein = SteinerNode(st_loc[0], st_loc[1])

        if with_obstacle and self.hasObstacles():
            #calc distances
            dist_steiner = (
                self.directDistance(neigh1, new_stein)
                + self.directDistance(neigh2, new_stein)
                + self.directDistance(neigh3, new_stein)
            )

            dist_original = (
                self.directDistance(neigh1, neigh2)
                + self.directDistance(neigh1, neigh3)
            )

            if dist_original < dist_steiner:
                return None
        #print(f'add steiner node (full) between {neigh1ind}, {neigh2ind} and {neigh3ind}')
        self.addSteinerNodeFull(new_stein, neigh1, neigh2, neigh3) #includes adding new edges

        #remove old edges
        self.removeEdge(neigh1ind, neigh2ind)
        self.removeEdge(neigh1ind, neigh3ind)

        return new_stein


    # ------------------------------------------------------------
    # inputRandSteiner: insert steiner at random load node or other steiner point angle which is less than 120 deg
    # if load node deg = 3 or higher the method finds the neighbouring 2 nodes that make the small angle
    # checks if corner point of new steienr becomes a false steiner
    # ------------------------------------------------------------
    def inputRandSteiner(self, with_steiner, MST_guaranteed, with_obstacle):
        print("input rand steiner")
        #list all possible nodes
        possible_nodes = self.getAllNodesWithSmallAngles(with_steiner)

        if not possible_nodes: #if there is no loadNode with a small angle stop
            print('no nodes with small angle, no mutate 3.')
            return None

        #choose random element from possible nodes
        neighind = random.choice(possible_nodes)

        if MST_guaranteed:
            print("input rand steiner, MST guaranteed")
            #removed neighind and replces it if it has become a false steiner node
            pair = self.insertSteinerHere(neighind, with_obstacle) #siplified consideration of obstacles

            if isinstance(pair.node, SteinerNode):
                return pair.node
        else:
            print("input rand steiner, MST not guaranteed")
            stein = self.insertForcedSteinerHere(neighind, with_obstacle)
            #this could have casued a steiner point of deg 2
            neighb = self.getNodeObject(neighind)
            if isinstance(neighb, SteinerNode):
                self.checkOrClearThis(neighb)

            return stein

        return None


    # ------------------------------------------------------------
    # inputAllSteiner: iteratively incldues steiner nodes at each small angle
    # ignores obstacles unless changed to true - if true a steiner node is only added if this would lead to a less expensive conenction
    # each time a Steiner point is added it checks and clears if the corner node has become a false Steiner point.
	# Note: Also SteinerPoints will be considered when looking for small angles. (Not just LoadNodes)
    # ------------------------------------------------------------
    def inputAllSteiner(self, with_obstacle=False):
        #list all possible nodes
        thispart = self.getAllNodesAsArray()
        possible_nodes = list(self.getNodesWithSmallAnglesIn(thispart))

        counter = 0
        maxloops = float("inf") #used as back up

        while possible_nodes: #as long as there are nodes with a small angle insert steiner nodes
            this_node = possible_nodes.pop(0)

            old_neighbours = [] #save all neighbours in case of deletion
            if isinstance(self.getNodeObject(this_node), SteinerNode):
                old_neighbours = list(self.adjList[this_node])

            #insert steiner point if necessary
            result = self.insertSteinerHere(this_node, with_obstacle)
            new_stein = result.node #returns null if no new steiner point was added
            #if thisNode was a steiner node it gets deleted and potentially replaced

            if result.option in (1, 2): #if steiner node sucessfully inserted
                new_index = self.getIndex(new_stein) #position of new index

                for neighb in self.adjList[new_index]: #updating the possible nodes, checking all neighbours of new steiner
                    is_small = self.hasSmallAngle(neighb)
                    is_contained = neighb not in possible_nodes

                    if is_small and is_contained:
                        possible_nodes.append(neighb)
                    elif not is_small and is_contained:
                        possible_nodes.remove(neighb)

            elif result.option == 3: #if rewired check for small angles in old neighbours
                for neighb in old_neighbours: #update possible nodes, check old neighbours of removed steiner node
                    is_small = self.hasSmallAngle(neighb)

                    if is_small and neighb not in possible_nodes:
                        possible_nodes.append(neighb)
                    elif not is_small and neighb in possible_nodes:
                        possible_nodes.remove(neighb)

            counter += 1
            if counter == maxloops:
                raise RuntimeError("Infinite loop safeguard triggered")


    # ------------------------------------------------------------
    # makeSteinerTree
    # removes all edges and makes a steiner minimal tree, does not consider obstacles
    # this also removes all obstacle nodes and all steienr nodes
    # ------------------------------------------------------------
    def makeSteinerTree(self):
        self.removeAllEdges()
        self.removeAllSteiners()
        self.removeAllObstacleNodes()
        self.MSTparts(self.nodes) #does not consider obstacels
        self.inputAllSteiner() #does not consider obstacles


    # ------------------------------------------------------------
    # calcTotalDistance
    # can consider obstacles, otherwise calculates euclidean distance
    # ------------------------------------------------------------
    def calcTotalDistance(self, consider_obstacles):

        total = 0.0

        for u, v in self.getAllEdges():
            node1 = self.getNodeObject(u)
            node2 = self.getNodeObject(v)

            if consider_obstacles:
                #print("Graph.calcTotalDist, direct distance of nodes ", u, " and ", v, " : ", self.directDistance(node1, node2))
                total += self.directDistance(node1, node2)
            else:
                #print("Graph.calcTotalDist, distance to of nodes ", u, " and ", v, " : ", self.directDistance(node1, node2))
                total += node1.distanceTo(node2)

        return total


    # ------------------------------------------------------------
    # plotGraph (matplotlib version)
    # ------------------------------------------------------------


    def plotGraph(self, title="", power_network=False):

        plt.figure()

        # plot nodes
        for i, node in enumerate(self.nodes):
            plt.scatter(node.x, node.y, c='blue')

        for j, Onode in enumerate(self.getAllObstacleNodes()):
            plt.scatter(Onode.x, Onode.y, c = 'red')

        # plot edges
        for u, v in self.getAllEdges():
            n1 = self.getNodeObject(u)
            n2 = self.getNodeObject(v)
            plt.plot([n1.x, n2.x], [n1.y, n2.y], color = 'black')

        if self.getNumberObstacles() >0:
            for obstacle in self.getObstacles():
                prev = obstacle.getPoints()[-1]
                for node in obstacle.getPoints():
                    #plt.scatter(node.x, node.y, color = 'grey')
                    if node is not prev:
                        plt.plot([node.x, prev.x], [node.y, prev.y], color = 'grey')
                    prev = node

        plt.title(title)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()


    def savePlot(self, name, file_loc, power_network=False, show=False):
        """
        Saves the graph as name.png in file_loc.
        Optionally displays it.
        """

        # Create figure (scale up like Java's *3 trick)
        plt.figure(figsize=(12, 12))

        # Draw graph (reuse your existing plotting logic)
        self.drawGraph(power_network)

        plt.title(name)

        # Ensure directory exists
        os.makedirs(file_loc, exist_ok=True)

        file_path = os.path.join(file_loc, f"{name}.png")

        try:
            plt.savefig(file_path, dpi=300)  # high resolution
            if show:
                plt.show()
            else:
                plt.close()
        except Exception as e:
            print("Image could not be saved")
            print(e)


    def drawGraph(self, power_network=False):
        """Helper used by both plot and save"""

        # draw nodes
        for node in self.nodes:
            plt.scatter(node.x, node.y)

        # draw edges
        for u, v in self.getAllEdges():
            n1 = self.getNodeObject(u)
            n2 = self.getNodeObject(v)
            plt.plot([n1.x, n2.x], [n1.y, n2.y])

        if self.getNumberObstacles() >0:
            for obstacle in self.getObstacles():
                prev = obstacle.getPoints()[-1]
                for node in obstacle.getPoints():
                    #plt.scatter(node.x, node.y, color = 'grey')
                    if node is not prev:
                        plt.plot([node.x, prev.x], [node.y, prev.y], color = 'grey')
                    prev = node




    class PathLength:
        def __init__(self, path, values):
            """
            path: list of Node
            values: list of distances
            """
            self.path = path
            self.values = values #values of distances between nodes
            self.value = sum(values) #total

            assert len(path) == len(values), "Path and values mismatch"

        def getPath(self):
            return self.path

        def getValue(self):
            return self.value

        def getValues(self):
            return self.values

        def reverse(self):
            # reverse path: reverse order of path and values
            path_rev = list(reversed(self.path))

            # reverse values (except the first which stays 0)
            #values_rev = [0.0] * len(self.values)
            #for i in range(1, len(self.values)):
            #    values_rev[i] = self.values[-i]
            values_rev = [0.0] + list(reversed(self.values[1:]))

            reversed_pl = Graph.PathLength(path_rev, values_rev)
            print(f'original path value: {self.value}, reversed path value: {reversed_pl.value}')

            assert abs(self.value - reversed_pl.value) < Graph.TOLERANCE
            return reversed_pl       
        

    class Edge:
        def __init__(self, one, two):
            self.one = one #node 1
            self.two = two #node 2

        def __hash__(self):
            # mimic Java's symmetric hash
            #return hash(self.one) // 10 + hash(self.two) // 10
            return hash(frozenset((self.one, self.two)))

        def __eq__(self, other):
            if not isinstance(other, Graph.Edge):
                return False
            return (
                (self.one is other.one and self.two is other.two)
                or (self.one is other.two and self.two is other.one)
            )


    class SPMap:
        def __init__(self): #maps 2 connections to its shortest path
            self.short_paths = {}

        def get(self, start, end):
            edge = Graph.Edge(start, end)
            sp = self.short_paths.get(edge)

            if sp is not None:
                # mimic Java static counters if you have them
                Graph.callsToSP += 1

                if sp.path[0] is not start:
                    sp = sp.reverse()

                assert (
                    sp.path[0] is start
                    and sp.path[-1] is end
                ), "Start/end incorrect"

            return sp

        def put(self, start, end, path_length):
            edge = Graph.Edge(start, end)
            self.short_paths[edge] = path_length

            Graph.numberSPcalcs += 1
            