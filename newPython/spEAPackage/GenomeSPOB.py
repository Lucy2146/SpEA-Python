import random
import copy

from .Graph import Graph
from .SteinerNode import SteinerNode
from .LoadNode import LoadNode


class GenomeSPOB(Graph):  # should inherit from your Graph class
    edgeCostsFactor = 9000.0
    instCap = 7.5 / 13.6986301

    #diversity factors for MG installation
    factor1 = 3.0/3.0
    factor2 = 2.57/3.0
    factor3 = 2.2/3.0
    factor4 = 2.0/3.0
    factor5 = 1.89/3.0
    factor6 = 1.8/3.0
    factor7 = 1.74/3.0
    factor8 = 1.71/3.0
    factor9 = 1.69/3.0
    factor10 = 1.64/3.0
    factor11 = 1.61/3.0
    factor12 = 1.57/3.0
    factor13 = 1.50/3.0
    factor14 = 1.46/3.0
    factor15 = 1.42/3.0
    factor16 = 1.40/3.0
    factor17 = 1.38/3.0
    factor18 = 1.37/3.0
    factor19 = 1.0/3.0

    MGCosts = 41000
    StartCost = 35000

    convCost = 0.25
    genCostMG = 0.03

    time_mg = 10.0
    time_network = 40.0

    OM_mg = 0.02
    OM_network = 0.02
    r_int = 0.01

    costs = -1

    smallestX = 10000
    smallestY = 10000
    largestX = 10
    largestY = 10




    def __init__(self, nodes, obstacles):
        super().__init__(nodes, obstacles)

        self.mutNumbers = [0, 0, 0, 0]
        self.costs = -1
        self.random = random.Random()    
        for node in self.getAllNodes():
            currentX = node.get_x()
            currentY = node.get_y()
            if currentX < self.smallestX:
                self.smallestX = currentX
            if currentX > self.largestX:
                self.largestX = currentX
            if currentY < self.smallestY:
                self.smallestY = currentY
            if currentY > self.largestY:
                self.largestY = currentY
        print(f'smallest x = {self.smallestX}, smallest y = {self.smallestY}, largest x = {self.largestX}, largest y = {self.largestY}')

    def __lt__(self, other):
        return self.costs < other.costs
    
    def __Ceq__(self, other):
        return self.costs == other.costs   
    
    def __eq__(self, other):
        return self is other
    
    def __hash__(self):
        return hash((self.getCosts(), str(self)))

    def clone(self):
        return copy.deepcopy(self)

    def getMutNr(self):
        return self.mutNumbers


    # Crossover option 1
    # Inspired by traditional one point crossover
    # Generate a random cut then swap the halves of each parent genome
    def crossover1(self, other):
        indiv1 = self.clone()
        indiv1.plotGraph(
            "Indiv1 pre",
            True
        )
        indiv2 = other.clone()
        indiv2.plotGraph(
            "Indiv2 pre",
            True
        )
        self.smallestX 
        xint = random.uniform(self.smallestX, self.largestX)
        #yint = random.uniform(self.smallestY, self.largestY) 
        # split parent 1 using the cut

        #split the nodes as obstacle nodes will be unique to that parent
        for node1 in indiv1.getIncludedObstacleNodes():
            if node1.get_x() > xint: #remove and add to other indiv
                indiv1.removeObstacleNode(node1)
                indiv2.addObstacleNode(node1)
            #else - if x < xint keep as is
        for node2 in indiv2.getIncludedObstacleNodes():
            if node2.get_x() > xint: #remove and add to other indiv
                indiv2.removeObstacleNode(node2)
                indiv1.addObstacleNode(node2)
            #else keep as is
        indiv1.plotGraph(
            "Indiv1 post",
            True
        )
        indiv2.plotGraph(
            "Indiv2 post",
            True
        )

        #split the edges
        #get all edges is a list of node index pairs from the adj list
        #pair is (i, j)
        

        return xint
        

    # ---------------------------
    # MUTATION 1: remove edge
    #If this removes an edge adjacent to a SteinerPoint, the SteinerPoint is removed and the other two nodes connected
	#If this causes an obstacle corner node to have degree 1, it will be removed as well
    # ---------------------------
    def mutate1(self):
        print(f'Mutate 1 occuring to an individual, count = {self.mutNumbers[0] + 1}')
        mutated = self.clone() #making a copy

        edges = mutated.getAllEdges() #list of all edges in the individual
        if not edges: #if there is no edge left, no mutation will occur
            return mutated #hence, return the individual which will be the same

        #choose a random edge
        edge = random.choice(edges)
        #remove this random edge
        mutated.removeEdgeAndReconnect(edge[0], edge[1], True)

        mutated.mutNumbers[0] += 1 #add to the counter for the number of times mutation 1 has happened
        return mutated

    # ---------------------------
    # MUTATION 2: connect components
    #adding an edge between two different connected components 
    #connect the shortest connection
    # ---------------------------
    def mutate2(self):
        print(f'Mutate 2 occuring to an individual, count = {self.mutNumbers[1] + 1}')

        mutated = self.clone() #make a copy

        #choose 2 random connected components
        components = mutated.getConnComponents()
        if len(components) <= 2: #if there are 1 or 2 components split using mutate 1 instead
            #promote further splitting
            return self.mutate1()

        # pick two components and connect closest nodes (this method ensures they are not the same)
        c1, c2 = random.sample(components, 2)

        best_pair = None #init node pairs to conenct
        best_dist = float("inf") #init best distance

        for n1 in c1: #for node in componenet 1
            node1 = mutated.getNodeObject(n1)
            if (isinstance(node1, SteinerNode)):
                continue #if node is a steiner point then skip that node

            for n2 in c2: #for node in component 2
                node2 = mutated.getNodeObject(n2)
                if isinstance(node2, SteinerNode):
                    continue #if node is a steiner point then skip that node

                d = node1.distanceSqrTo(node2) #calc distance between 2 nodes
                if d < best_dist: #update best distance and node pair
                    best_dist = d
                    best_pair = (n1, n2)

        if best_pair:
            mutated.addEdge(best_pair[0], best_pair[1]) #if the best then connect nodes with an edge

        mutated.mutNumbers[1] += 1 #add to counter for mutation 2
        return mutated

    # ---------------------------
    # MUTATION 3: add Steiner node
    # Introduces a random Steiner Point somewhere at a small angle (including angles at already existing Steiner Points)
	# but only if this won't hit an obstacle (i.e. only if it reduces length)
	# After inserting a Steiner Point always check whether this point has caused a
    # different Steiner Point to be of degree2 and remove this one.
    # ---------------------------
    def mutate3(self):
        print(f'Mutate 3 occuring to an individual, count = {self.mutNumbers[2] + 1}')
        mutated = self.clone()

        # remove edge and insert Steiner node 
        # withSteiner = first = true means Steiner Points get inserted at small angles of other Steiner Points
        # MSTguaranteed = second = false means that the possible conenction may not be minimal
        # withObstacle = third = true means obstacles are consiered
        s = mutated.inputRandSteiner(True, False, True)

        mutated.mutNumbers[2] += 1 #add 1 to counter for mutation 3
        return mutated
    
    # ---------------------------
    # MUTATION 4: Remove a random Steiner Point
    # Also check its neighbours for potential false Steiner Points
    # Warning? By removing a Steiner Point one can cause obstacle corner points to be degree 1
    # ---------------------------
    def mutate4(self):
        print(f'Mutate 4 occuring to an individual, count = {self.mutNumbers[3] + 1}')

        nrSteiner = len(self.steinerPoints)
        if ( nrSteiner == 0):
            return self.mutate3() # if no steiner points add one instead
        
        mutated = self.clone() #make a copy

        #choose a random steiner point
        randomSteiner = random.randrange(nrSteiner)
        steiner_tm = mutated.steinerPoints[randomSteiner] #get point
        steiner_ind = mutated.getIndex(steiner_tm) #get points index

        # Save neighbours that is connected to that Steiner
        neighbours = []
        for neighb_ind in mutated.adjList[steiner_ind]: #for neighbour in the steiner points adjacency list
            neighbours.append(mutated.getNodeObject(neighb_ind)) #add to neighbour list

        # Remove Steiner node (also removes edges)
        #this might cause a false Steiner Point
        mutated.removeSteinerNode(steiner_tm)

        # Clean up neighbouring Steiner nodes if needed
        for neighb in neighbours:
            if isinstance(neighb, SteinerNode):
                mutated.checkOrClearThis(neighb) #for node in neighbours clean up the connections
                #this may cause obstacle corners of degree 1

        mutated.mutNumbers[3] += 1 #add to mutation 4 counter

        return mutated


    # ---------------------------
    # MAIN MUTATION WRAPPER
    # ---------------------------
    def mutate(self, p1, p2, p3):
        r = random.random()

        if r < p1:
            return self.mutate1()
        elif r < p1 + p2:
            return self.mutate2()
        elif r < p1 + p2 + p3:
            return self.mutate3()
        else:
            return self.mutate4()

    # ---------------------------
    # LARGE STEP MUTATION
    # ---------------------------
    def largeMutate(self, steps, p1, p2, p3):
        g = self.clone()
        for _ in range(steps): #do multiple mutations until step size reached
            g = g.mutate(p1, p2, p3)
        return g

    # ---------------------------
    # COMPARISON (TreeSet equivalent)
    # ---------------------------
    #def __lt__(self, other):
    #    return self.costs < other.costs

   #def __eq__(self, other):
   #     return isinstance(other, GenomeSPOB) and self.costs == other.costs

    def calcSimpleCosts(self, just_distance, timeFrame):

        # --------------------------------------------
        # edge distance cost
        # --------------------------------------------
        total_distance = 0.0

        for u, v in self.getAllEdges():

            node1 = self.getNodeObject(u)
            node2 = self.getNodeObject(v)

            #if consider_obstacles:
            dist = self.directDistance(node1, node2)
            #else:
            #    dist = node1.distanceTo(node2)

            total_distance += dist

        # --------------------------------------------
        # connectivity penalty
        # --------------------------------------------
        num_components = self.nrConnComponents()
        #print("total distance from GENOMESPOB.CalcCosts: ",total_distance)
        #print("number of components from GenomeSPOB.calcCosts: ", num_components)
        alpha = 10000.0

        component_penalty = alpha * (num_components - 1)

        # --------------------------------------------
        # final cost
        # --------------------------------------------
        self.costs = total_distance + component_penalty

        return self.costs
    
    # --------------------------
    # CALC COSTS
    # justDistance = true means the total cost is just the length of the graph
    # if obstacles are present they are considered
    # timeFrame = number of years for consideration
    # --------------------------
    def calcCosts(self, justDistance, timeFrame):
        #print("start calc cost")
        withObstacles = self.hasObstacles() #checking if individual has obstacles

        if(justDistance):
            #print("CalcCost of Genome using only distance")
            self.costs = self.calcTotalDistance(withObstacles) #if just using distances (not weighted costs) then calc distance with or without obstacles
        #print("using full cost function")

        instCostMG = 0 #installation costs for MG
        networkCosts = 0 #network costs, based on distance?
        fuelCosts = 0 #yearly fuel cost

        allEdges = self.getAllEdges()
        for edge in allEdges:
            node1 = self.getNodeObject(edge[0])
            node2 = self.getNodeObject(edge[1])

            if withObstacles:
                #print("CaclCosts of genome with obstacles, using directDist")
                distance = self.directDistance(node1, node2)
            else:
                distance = node1.distanceTo(node2)

            networkCosts += distance * self.edgeCostsFactor

        # ------------------------------------------------------------
        # Connected components
        # ------------------------------------------------------------
        partition = self.getConnComponents()
        #print("number of partitions: ", len(partition))

        for part in partition:
            # --------------------------------------------------------
            # Non-microgrid component
            # (contains main grid node 0)
            # --------------------------------------------------------
            if 0 in part:

                for i in part:

                    nodei = self.getNodeObject(i)

                    if isinstance(nodei, LoadNode):

                        # load assumed kWh/day
                        fuelCosts += (
                            self.convCost * 365.0 * nodei.getLoad())

            # --------------------------------------------------------
            # Microgrid component
            # --------------------------------------------------------
            else:

                loadInPart = 0.0

                # Fuel costs
                for i in part:

                    nodei = self.getNodeObject(i)

                    if isinstance(nodei, LoadNode):

                        fuelCosts += (
                            self.genCostMG
                            * 365.0
                            * nodei.getLoad()
                        )

                        loadInPart += nodei.getLoad()

                # ----------------------------------------------------
                # Installation costs
                # ----------------------------------------------------
                nrCust = len(part) #number of customers in that MG

                # diversity factor lookup
                factor_lookup = {
                    1: self.factor1,
                    2: self.factor2,
                    3: self.factor3,
                    4: self.factor4,
                    5: self.factor5,
                    6: self.factor6,
                    7: self.factor7,
                    8: self.factor8,
                    9: self.factor9,
                    10: self.factor10,
                    11: self.factor11,
                }

                instFactor = factor_lookup.get(nrCust, 0.0)

                # larger customer groups
                if instFactor == 0.0 and nrCust > 0:

                    if nrCust <= 14:
                        instFactor = self.factor12

                    elif nrCust <= 17:
                        instFactor = self.factor13

                    elif nrCust <= 20:
                        instFactor = self.factor14

                    elif nrCust <= 23:
                        instFactor = self.factor15

                    elif nrCust <= 26:
                        instFactor = self.factor16

                    elif nrCust <= 29:
                        instFactor = self.factor17

                    elif nrCust <= 59:
                        instFactor = self.factor18

                    else:
                        instFactor = self.factor19

                instCostMG += (
                    self.StartCost
                    + self.MGCosts
                    * instFactor
                    * self.instCap
                    * loadInPart
                )

        # ------------------------------------------------------------
        # Net Present Value factor
        # ------------------------------------------------------------
        npv_factor = (
            (1.0 - (1.0 + self.r_int) ** (-timeFrame))
            / self.r_int
        )


        # ------------------------------------------------------------
        # Final cost calculation
        # ------------------------------------------------------------
        self.costs = (
            npv_factor
            * (
                (instCostMG * self.OM_mg + instCostMG / self.time_mg)
                + (
                    networkCosts * self.OM_network
                    + networkCosts / self.time_network
                )
            )
            + timeFrame * fuelCosts
        )
        #print("end calc costs")
        return self.costs



    def getCosts(self):
        return self.costs
    
    '''def compareTo(self, other):
        a = self.getCosts()
        b = other.getCosts()
        #campring using costs hence the higher value should be lower in rank
        if (a.compareTo(b) != 0):
            return a.compareTo(b)
        return '''
