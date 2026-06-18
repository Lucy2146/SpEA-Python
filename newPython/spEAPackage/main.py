#run using:        uv run python -m spEAPackage.main NewExample 1
# called from newPython


import sys
import time
from pathlib import Path

from .CSVReadWrite import CSVreadWrite
from .Graph import Graph
from .GenomeSPOB import GenomeSPOB
from .AlgorithmSPOB import AlgorithmSPOB


class Main:

    # ============================================================
    # DEFAULT SETTINGS
    # ============================================================

    DATASET = "SoftObstacles"
    INSTANCE = 1

    # command line arguments
    if len(sys.argv) > 1:
        DATASET = sys.argv[1]

    if len(sys.argv) > 2:
        INSTANCE = int(sys.argv[2])

    # ============================================================
    # EA PARAMETERS
    # ============================================================

    POPULATION_SIZE = 10
    TOURN_SIZE = 2
    MUTATE_NR = 5
    OFFSPRING_PP = 1

    # GA parameters
    LARGE_STEP_MUTATE_NR = MUTATE_NR // 3
    STEP_SIZE = 5

    GA_PROB1 = 0.50
    GA_PROB2 = 0.20
    GA_PROB3 = 0.20

    # fixed parameters
    LIFESPAN = 20
    CRITERIA = 100 # number of generations to go through before checking stopping criteria
    DIFFERENCE = 0.01 #0.01     #difference between generations in order to stop

    # flags
    PRINT_OUT = True
    PRINT_INPUT = False

    # ============================================================
    # MAIN
    # ============================================================

    @staticmethod
    def main():

        # --------------------------------------------------------
        # paths
        # --------------------------------------------------------

        BASE_DIR = Path(__file__).resolve().parent

        DATA_DIR = BASE_DIR / "data" / Main.DATASET
        #DATA_DIR = "./data/NewExample"
        RESULTS_DIR = BASE_DIR / "results" / Main.DATASET
        PLOTS_DIR = BASE_DIR / "plots" / Main.DATASET

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        PLOTS_DIR.mkdir(parents=True, exist_ok=True)

        print(f"\nDataset: {Main.DATASET}")
        print(f"Instance: {Main.INSTANCE}\n")

        # --------------------------------------------------------
        # filenames
        # --------------------------------------------------------

        input_nodes = f"terminals{Main.INSTANCE}.csv"
        input_obstacles = f"obstacles{Main.INSTANCE}.csv"

        output_name = f"SPOB_convergence_{Main.DATASET}_{Main.INSTANCE}"

        save_output = RESULTS_DIR / f"{output_name}.csv"

        # --------------------------------------------------------
        # read terminals
        # --------------------------------------------------------

        nodes = CSVreadWrite.read_nodes_from_file(
            str(DATA_DIR),
            input_nodes, #terminals1.csv
            Main.PRINT_INPUT
        )
        #print(nodes)
        # --------------------------------------------------------
        # read obstacles
        # --------------------------------------------------------

        obstacle_file = DATA_DIR / input_obstacles

        if obstacle_file.exists():

            obstacles = CSVreadWrite.read_obstacles_from_file(
                str(DATA_DIR),
                input_obstacles,
                Main.PRINT_INPUT
            )

        else:
            obstacles = []

        with_obstacles = len(obstacles) > 0

        if with_obstacles:
            print("Obstacles are considered.")
        else:
            print("Obstacles are NOT considered.")

        # --------------------------------------------------------
        # run EA
        # --------------------------------------------------------

        Main.runEA(
            nodes,
            obstacles,
            save_output,
            output_name,
            PLOTS_DIR
        )

        # --------------------------------------------------------
        # debug / stats
        # --------------------------------------------------------

        n = len(nodes)
        exp_calcs = n * (n - 1) // 2

        print("\n\nNumber of shortest paths calculations:",
              Graph.numberSPcalcs)

        print("Expected maximum number:", exp_calcs)

        print("Number of shortest path calls:",
              Graph.callsToSP)

        print("Shortest paths between non-terminals:",
              Graph.nonloads)

        print("\nFinished spEA!")

    # ============================================================
    # RUN EA
    # ============================================================

    @staticmethod
    def runEA(
        nodes,
        obstacles,
        save_output,
        plot_name,
        plot_path
    ):

        # --------------------------------------------------------
        # initial solution
        # --------------------------------------------------------

        optimised_start = GenomeSPOB(nodes, obstacles)
        optimised_start.plotGraph(
            "Initial Network: Pre Start",
            True
        )
        optimised_start.MSTWithObstacles(nodes)
        optimised_start.plotGraph(
            "Initial Network: Post MST",
            True
        )

        initial_costs = optimised_start.calcCosts(True, Main.LIFESPAN)

        # --------------------------------------------------------
        # plot + print
        # --------------------------------------------------------

        '''optimised_start.plotGraph(
            "Initial Network: Optimised Start",
            True
        )
        friend = optimised_start.mutate1()
        friend.plotGraph(
            "Mutated Friend Network",
            True
        )
        #mute = optimised_start.crossover1(friend)
        #print(f"mute: {mute}")
        print(friend.adjList)
        friend = friend.mutate3()
        print(friend.adjList)

        print(optimised_start)
        
        mutated1 = optimised_start.mutate3()
        mutated1.plotGraph(
            "Mutated Initial Network",
            True
        )
        print(mutated1)
        

        mutated1 = mutated1.mutate4()
        mutated1.plotGraph(
            "Mutated Initial Network",
            True
        )'''
        
        print("Initial costs:", initial_costs)

        # --------------------------------------------------------
        # save initial output
        # --------------------------------------------------------

        first_row = "Generation,Lowest Cost"
        second_row = f"0,{initial_costs}"

        entry = (
            first_row
            + "\n"
            + second_row
        )

        CSVreadWrite.write_output(
            str(save_output),
            entry,
            create_new_file=True
        )

        # --------------------------------------------------------
        # start timer
        # --------------------------------------------------------

        start_time = time.time()
        print("Starting timer for Algorithm")

        # --------------------------------------------------------
        # initialise algorithm
        # --------------------------------------------------------

        alg = AlgorithmSPOB(
            optimised_start,
            Main.POPULATION_SIZE,
            Main.LIFESPAN,
        )
        print("finish init")

        alg.setParameters(
            Main.GA_PROB1,
            Main.GA_PROB2,
            Main.GA_PROB3,
            Main.TOURN_SIZE,
            Main.MUTATE_NR,
            Main.OFFSPRING_PP,
            Main.LARGE_STEP_MUTATE_NR,
            Main.STEP_SIZE,
        )
        #print("finish set param")

        initial_best = alg.lowestCost()

        print(
            f"Generation: {alg.count}"
            f"\tLowest Cost: {initial_best}"
        )

        # --------------------------------------------------------
        # debug print
        # --------------------------------------------------------

        print("\nPopulation sample:")

        for i, cost in enumerate(alg.getPopulationValues()):

            print(cost, end=" - ")

            if i >= 29:
                break

        print("\n")
        #alg.getFitnessEvals()
        #print("\n")
        #alg.printCurrentPopValues()

        # --------------------------------------------------------
        # run algorithm
        # --------------------------------------------------------
        print("starting the run")
        builder = alg.run(
            Main.CRITERIA,
            Main.DIFFERENCE,
            Main.PRINT_OUT
        )

        # --------------------------------------------------------
        # end timer
        # --------------------------------------------------------

        end_time = time.time()

        # --------------------------------------------------------
        # save output
        # --------------------------------------------------------

        CSVreadWrite.write_output(
            str(save_output),
            builder,
            create_new_file=False
        )

        # --------------------------------------------------------
        # final stats
        # --------------------------------------------------------

        print(f"\n\nAlgorithm ended after {alg.count} generations.")

        print(f"Best cost: {alg.lowestCost()}")

        improved_by = (
            100.0
            * (1.0 - (alg.lowestCost() / initial_costs))
        )

        improved_by = int(improved_by * 1000) / 1000.0

        print(f"Improvement: {improved_by}%")

        # --------------------------------------------------------
        # final graph
        # --------------------------------------------------------

        final_graph = alg.bestGenome()

        final_graph.savePlot(
            plot_name,
            str(plot_path),
            True,
            True
        )

        # --------------------------------------------------------
        # mutation stats
        # --------------------------------------------------------

        print("\nFinal graph mutations:")

        for i, val in enumerate(final_graph.getMutNr()):

            print(f"mutation {i+1}: {val}", end="\t")

        print()

        # --------------------------------------------------------
        # debug again
        # --------------------------------------------------------

        print("\nPopulation sample:")

        for i, cost in enumerate(alg.getPopulationValues()):

            print(cost, end=" - ")

            if i >= 29:
                break

        # --------------------------------------------------------
        # elapsed time
        # --------------------------------------------------------

        elapsed = end_time - start_time

        print(f"\nElapsed time (ms): {int(elapsed * 1000)}")

        print(f"Elapsed time (s): {elapsed}")


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":
    Main.main()