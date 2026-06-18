import random
from bisect import insort
from collections import deque
import math
import time


class AlgorithmSPOB:
    def __init__(self, optimised, population_size, life_span):
        #optimised should be a connected graph
        #population_size is pop size
        #life_span is life span
        self.PROBMut1 = 0.50 #probability to do mutation 1: remove an edge
        self.PROBMut2 = 0.20 # prob to do mut 2: add an edge
        self.PROBMut3 = 0.20 # prob to do mut 3: add a Steiner Point
        #prob to do mutation 4:remove a Steiner Point = 1 - PROBMut1 - PROBMut2 - PROBMut3

        self.random = random.Random()

        self.stepSIZE = 5 #step size of large mutation - how many consecutive mutations to do without reevaluation

        self.popSize = population_size #population size max?
        self.lifeSpan = life_span

        self.withObstacles = optimised.hasObstacles()

        self.tournSize = 10 #tournament size
        self.parentNr = 10 #number of parents allowed to mutate
        self.offspringPP = 1 #number of offspring per parent
        self.largeStepMutateNr = 3 #how many allowed to large step mutate

        self.DISTANCEinsteadofCOST = False #if true the distance is used as the cost measure
        #should be false when using proper cost function

        self.noFitnessEvals = 0 #counting number of cost evaluations the algorithm does
        self.count = 0 #counting how many generations the algorithm goes through

        # Python replacement for TreeSet → sorted list
        self.population = []

        initStart = time.time()
        # evaluate initial genome
        optimised.calcCosts(self.DISTANCEinsteadofCOST, life_span)
        self.noFitnessEvals += 1 #add to counter for cost evaluations
        self.addToPopulation(optimised) #add optimised to population of this algorithm run ('self')
        print(f"initial genome done: {time.time()-initStart}")


        # --- Initialisation of Population ---
        # Precambrian Explosion using only the first 2 mutation types
        # first portion of pop filled by mutation 1, second half fileld with mutation 2
        i = 0
        while len(self.population) < self.popSize // 4:#4: #do until the pop size is portion of max
            pop = len(self.population)
            newG = optimised.mutate(1.0, 0.0, 0.0) #only the first mutation, hence prob mut 1 = 1, others = 0
            newG.calcCosts(self.DISTANCEinsteadofCOST, life_span) #recalc costs
            self.noFitnessEvals += 1 #add to cost eval counter
            self.addToPopulation(newG) #add new
            if len(self.population) == pop:
                i +=1 #count up number of rounds where no new individual is added
            if i > 150: 
                print("While in pop init, precambrian explosian become infinite, It has been ended early")
                break
            #print('length of pop from precambrian: ', len(self.population))
        print(f"first quarter filled by mutations: {time.time() - initStart}")

        i = 0
        while len(self.population) < self.popSize: #do until the full population is filled
            pop = len(self.population)
            thisG = random.choice(self.population) #select randomly of the previously generated
            newG = thisG.mutate(0.90, 0.10, 0.0) #mutate
            newG.calcCosts(self.DISTANCEinsteadofCOST, life_span)
            self.noFitnessEvals += 1
            self.addToPopulation(newG)

            if len(self.population) == pop:
                i +=1 #count up number of rounds where no new individual is added
            if i > 150: 
                print("While in pop init, filling remainder of pop become infinite, It has been ended early")
                break
        print(f"last of init population filled: {time.time()-initStart}")
        print("Population size: ", len(self.population), "\n")
    # --- TreeSet behaviour ---
    def addToPopulation(self, genome): #adding to list while maintaining order
        
        if genome not in self.population:
            #print("added to population: ", genome)
            insort(self.population, genome)
        #else: print("could not add to population: ", genome)

    def setParameters(self, PROBMut1, PROBMut2, PROBMut3, tournSize, parentNr, OffspringPP, largeStepMutNr, stepSize):
        self.PROBMut1 = PROBMut1
        self.PROBMut2 = PROBMut2
        self.PROBMut3 = PROBMut3      

        assert (
            PROBMut1 + PROBMut2 + PROBMut3 <= 1.0
        ), "Incorrect probabilities"

        #assert self.popSize >= 10, ""

        self.tournSize = tournSize

        assert (
            tournSize >= 2
        ), "If the tourn size is smaller than 2: No guarantee for keeping the best genome"

        self.parentNr = parentNr

        assert (
            parentNr >= 1
        ), "You are not doing mutations."

        self.largeStepMutateNr = largeStepMutNr

        assert (
            largeStepMutNr > 0
        ), "Incorrect large-step mutation number."

        self.offspringPP = OffspringPP

        assert (
            OffspringPP >= 1
        ), "You are not creating any new offspring."

        offspringSize = parentNr * OffspringPP + largeStepMutNr

        assert (
            offspringSize <= self.popSize
        ), "The offspring size cannot exceed the population size."

        self.stepSIZE = stepSize

        assert self.stepSIZE >= 2, ""

    def selectN(self, n):
        #selecting n random genomes from the population and returning them in a sorted tree
        selection = self.population[:] #getting whole population
        random.shuffle(selection) #shuffle selection
        selection = selection[:n] #select n from the shuffled list
        return sorted(selection) #returns sorted list of n genomes

    def selection(self, how_many, tourn_size, best=True):
        #performing a stochastic tournament on the population set
        #to delete high cost and adding new genomes
        selected = set()
        #print("selecting ", how_many, " from population")
        i = 0
        while len(selected) < how_many: #while you have selected less than the allowed number of tournaments
            #print("continuing while for selection")
            tournament = self.selectN(tourn_size) #choose n genomes
            #print(f"Winner ID: {id(tournament[0])} | Already in set: {tournament[0] in selected}")
            
            pop = len(selected)
            if best:
                #print("add to beginning of pop")
                selected.add(tournament[0]) #if selecting the best during the tournament add to beginning of list
            else:
                #print("adding to end of pop")
                selected.add(tournament[-1]) #else add to end of chosen genome list
            #print("returning to top of while in selection, selected so far: ", len(selected))
            
            if len(selected) == pop:
                i +=1 #count up number of rounds where no new individual is added
            if i > 150: 
                print("While in selection became infinite. ", how_many, " individuals wanted, ", pop, " individuals found.")
                break

        #print("while broken in selected, finish selection")
        return selected

    def nextGen(self):
        #replaces population with next generation
        #print("choosing genes to mutate")
        to_mutate = self.selection(self.parentNr, self.tournSize, True) #choose genomes to mutate and produce offspring
        
        #print("choosing genes for large mutate")
        to_step_mutate = self.selection(self.largeStepMutateNr, self.tournSize, True) #choose genomes to compelte large step size mutations
        offspring = [] #new array for offspring
        #print("adding genomes to offspring single mut")
        # normal single mutation 
        for geno in to_mutate: #for genome in the subset allowed to mutate
            for _ in range(self.offspringPP): #if the number of offspring is less than allowed
                offspring.append(
                    geno.mutate(self.PROBMut1, self.PROBMut2, self.PROBMut3)
                ) #add mutated genome to list of offspring

        # large step mutation - mutated several times
        #print("adding genome for large scale")
        for geno in to_step_mutate:
            offspring.append(
                geno.largeMutate(
                    self.stepSIZE,
                    self.PROBMut1,
                    self.PROBMut2,
                    self.PROBMut3,
                )
            )
        #print(f"next gen offspring: {len(offspring)}, to mutate: {len(to_mutate)}, to large step size mutate: {len(to_step_mutate)}")
        
        #print("choosing genomes to die")
        # remove worst (ensuring elitism where best solutions do not die off)
        to_die = self.selection(len(offspring), self.tournSize, False) #select as many genomes as children so the pop size remains consistent
        #print("next gen, to die: ", len(to_die))
        self.population = [g for g in self.population if g not in to_die] #remove back sol from pop

        #print("calc cost of offspringgenome")
        # evaluate each new offspring + insert into population
        for genome in offspring:
            genome.calcCosts(self.DISTANCEinsteadofCOST, self.lifeSpan)
            self.noFitnessEvals += 1 #add to cost eval counter
            self.addToPopulation(genome)

        self.count += 1 #add to generation counter
        #print("end of next gen funct")

    def bestGenome(self):
        return self.population[0] #return the first genome from the order population list

    def lowestCost(self):
        return self.population[0].costs #return self.best_genome.costs
    

    def run(self, stopCriteria, difference, printOut):
        """
        Run the evolutionary algorithm until improvement is below threshold.

        Parameters
        ----------
        stopCriteria : int
            Number of generations to compare over.
        difference : float
            Percent difference threshold for stopping.
        printOut : bool
            Whether to print progress.

        Returns
        -------
        str
            CSV-style string of generation,cost
        """
        runStart = time.time()

        # store results as strings
        rows = []

        # queue of recent best results
        lastResults = deque()

        # initial value
        initial_best = self.lowestCost()
        lastResults.append(initial_best)

        totalDifference = float("inf")

        # output initial generation
        if printOut:
            timeSince = time.time() - runStart
            print(f"Generation: {self.count}\t\tPopulation Size: {len(self.population)}\t\tLowest Cost: {initial_best}\t\tTime Elapsed: {timeSince}")

        rows.append(f"{self.count},{initial_best}")
        #print("start while in run")
        while totalDifference > difference:
            #print("start of next while")
            # create next generation

            self.nextGen()
            #print("next gen created")

            newBest = self.lowestCost()
            #print("new best lowest cost calculated")

            lastResults.append(newBest)
            #print("new best added to results")

            # update stopping condition
            if self.count >= stopCriteria:
                #print("if count greater than stopping criteria, continue")

                # keep only most recent values
                lastResults.popleft()

                # avoid division by zero
                if abs(newBest) < 1e-12:
                    totalDifference = 0.0
                    #print("total difference is close to 0, so set as 0")
                else:
                    totalDifference = (
                        100.0
                        * abs(lastResults[0] - lastResults[-1])
                        / abs(newBest)
                    )
                    #print("total difference is non zero: ", totalDifference)

                if printOut:
                    print(f"total difference: {totalDifference}")

            # print progress
            if printOut:
                print(f"Generation: {self.count}\t\tPopulation Size: {len(self.population)}\t\tLowest Cost: {newBest}\t\tTime Elapsed: {time.time()-runStart}")

            #print("end of this while cycle?")
            rows.append(f"{self.count},{newBest}")
            #print("return to top")
        #print("end while in run")
        # return CSV-style string
        return "\n".join(rows)


    def getFitnessEvals(self):
        """
        Returns the number of fitness evaluations.
        """
        return self.noFitnessEvals


    def printCurrentPopValues(self):
        """
        Testing/debugging function.
        Checks whether stored fitness values are correct.
        """

        allValues = []
        allRealValues = []

        for element in self.population:

            # stored value
            allValues.append(element.getCosts())

            # recalculate
            element.calcCosts(
                self.DISTANCEinsteadofCOST,
                self.lifeSpan
            )

            allRealValues.append(element.getCosts())

        print("The genomes in the current population carry the following cost values:")
        print(allValues)

        print("This should be the same as:")
        print(allRealValues)


    def getPopulationValues(self):
        """
        Returns list of population costs.
        """

        allCosts = []

        for item in self.population:
            allCosts.append(item.getCosts())

        return allCosts
    
    
    #def getPopSize
