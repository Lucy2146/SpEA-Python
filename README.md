# SpEA-Python
SpEA Algorithm Python Implementation

This repository is based on the SpEA algorithm developed by Manou Rosenburg. The algorithm optimally clusters and connects a set of nodes, the purpose is to design optimal electricity distribution networks.

To run:  uv run python -m spEAPackage.main NewExample 1

NewExample = name of data set using -> folder name in data
in this folder there should be 
* Connections.csv = the edge list of the initial (not necessary)
* terminals1.csv = list of nodes in the format: X coord, Y coord, Load
* obstacles1.csv = list of obstacles in the format: weight of obstacle 1
                                                    X coord 1, Y coord 1

                                                    weight of obstacle 2
                                                    X coord 2, Y coord 2 ...

  
