import os
import numpy as np
import pandas as pd
import math
import random
from random import sample
from timeit import default_timer as timer

'''
Initialize First Generation
    Endure Life -> survive?
        - What is it to live? What kind of hardships, evaluations? And based on features will these organisms be tested?
            - What are the features of each organism and how are they derived?
                - Features are pre-binned
    Attempt Reproduction -> get it in?
    Reproduce -> hopefully viable!
'''

# Globals
counter = 1000
current_year = 0
total_pop = 0  # Max Environment can handle


def inherit(p1, p2, genome=False):
    # Take a random sample of indices of list
    child = []
    randomIndices = sample(range(len(p1)), len(p1) // 2)
    for i in range(len(p1)):
        if i in randomIndices:
            # Add from p1
            child.append(p1[i])
        else:
            # Add from p2
            child.append(p2[i])

    if genome:
        child = ''.join(child)
    return child


def mutate_genome(genome, mutation_matrix):
    # Base Dict
    bases = {
        0: "A",
        1: "T",
        2: "C",
        3: "G"
    }

    # Gen random num of range and check if it is greater or less then mutation matrix for that element
    out_genome = ""
    for index, ele in enumerate(mutation_matrix):
        randInt = random.randint(0, 20)
        if randInt > 20 * ele:
            out_genome += bases[int(randInt % 4)]
        else:
            out_genome += genome[index]
    return out_genome


def mutate_matrix(mutation_matrix):
    for i in range(len(mutation_matrix)):
        localRandomValue = random.randint(0, 5)
        localRandomValue = localRandomValue / 100
        coinflip = random.randint(0, 100)
        if coinflip > 50:
            mutation_matrix[i] = mutation_matrix[i] + localRandomValue
        else:
            mutation_matrix[i] = mutation_matrix[i] - localRandomValue
    return mutation_matrix


def parseGenome(genome):
    # Behavior: Hostile / Timid

    def generateParseDict():
        base_list = ['A', 'T', 'C', 'G']

        new_dict = {}

        counter = 0.5

        for base1 in base_list:
            for base2 in base_list:
                new_dict[base1 + base2] = counter
                counter += 0.5

        return new_dict

    # {'AA': 0.5, 'AT': 1.0, 'AC': 1.5, 'AG': 2.0, 'TA': 2.5, 'TT': 3.0, 'TC': 3.5, 'TG': 4.0, 'CA': 4.5, 'CT': 5.0,
    # 'CC': 5.5, 'CG': 6.0, 'GA': 6.5, 'GT': 7.0, 'GC': 7.5, 'GG': 8.0}

    parseDict = generateParseDict()

    output_list = []

    # Check Valid Primer
    if genome[:3] == "ATC":
        # Valid
        # Evaluate Behavior
        output_list.append(parseDict[genome[4:6]])
        # Evaluate Size
        output_list.append(parseDict[genome[7:9]])
        # Evaluate Speed
        output_list.append(parseDict[genome[10:12]])
        # Evalute Sight
        output_list.append(parseDict[genome[13:15]])
    else:
        output_list = ["NonViable" for x in range(4)]

    if any(["NonViable" for x in output_list if x == 0.5 or x == 8]):
        output_list = ["NonViable" for x in range(4)]

    return output_list


def randomPosition(grid):
    notFound = True
    while notFound:
        y_temp = random.randint(0, np.size(grid[0]) - 1)
        x_temp = random.randint(0, np.size(grid[0]) - 1)
        if grid[y_temp][x_temp] == 0:  # Is Empty
            return [y_temp, x_temp]


def findNearestEmpty(grid, p1coors, p2coors):
    # search around parents
    for i in range(-1, 1):
        for j in range(-1, 1):
            if grid[p1coors[0] + i][p1coors[1] + j] == 0:
                if not any(x == -1 or x == np.size(grid) + 1 for x in [p1coors[0] + i, p1coors[1] + j]):
                    return [p1coors[0] + i, p1coors[1] + j]
            if grid[p2coors[0] + i][p2coors[1] + j] == 0:
                if not any(x == -1 or x == np.size(grid) + 1 for x in [p2coors[0] + i, p2coors[1] + j]):
                    return [p2coors[0] + i, p2coors[1] + j]


class Organism:
    # Implement Binary Tree genealogy

    def __init__(self, parent1=None, parent2=None, first_gen=False, Grid=None):
        global counter
        global current_year
        # Self Initialization
        # Inherit Mutation Matrix
        # Then mutate their genome
        if first_gen:
            tempGenome = "ATCTGTTGGTGATGATGA"
            tempMutation_Matrix = [0.5 for r in range(17)]
            self.parent1id = parent1
            self.parent2id = parent2

            if Grid is None:
                self.position = [0, 0]  # y, x
            else:
                self.position = randomPosition(Grid)
            # Find the empty tile nearest both parents
        else:
            tempGenome = inherit(parent1.Genome, parent2.Genome, genome=True)  # function for inheritance
            tempMutation_Matrix = inherit(parent1.mutation_matrix, parent2.mutation_matrix)
            self.parent1id = parent1.id
            self.parent2id = parent2.id
            if Grid is None:
                self.position = [0, 0]
            else:
                self.position = findNearestEmpty(Grid, parent1.position, parent2.position)
            # Find Random position on Grid

        self.mutation_matrix = mutate_matrix(tempMutation_Matrix)
        self.Genome = mutate_genome(tempGenome, self.mutation_matrix)

        # Initialize features / behaviors from Genome
        features = parseGenome(self.Genome)
        self.behavior = features[0]
        self.size = features[1]
        self.speed = features[2]
        self.vision = 2

        # Check if Viable
        if "NonViable" in features:
            self.viable = False
            self.alive = False
            self.murderer = "NonViable"
            self.resource_demand = 0
        else:
            self.viable = True
            self.alive = True
            self.murderer = None
            self.resource_demand = (self.size ** 3) * (self.speed ** 2)

        self.current_resources = 0
        self.fights = 0
        self.escapes = 0
        self.id = counter + 1
        self.mate = None
        self.birthyear = current_year
        self.age = 0

        counter += 1

    def add_resources(self, amount):
        self.current_resources += amount

    def reset_resources(self):
        self.current_resources = 0

    def to_dict(self):
        return {
            "ID": self.id,
            "Birth Year": self.birthyear,
            "Age": self.age,
            "Genome": self.Genome,
            "MutationMatrix": self.mutation_matrix,
            "Parent1": self.parent1id,
            "Parent2": self.parent2id,
            "Behavior": self.behavior,
            "Size": self.size,
            "Speed": self.speed,
            "Resources Required": self.resource_demand,
            "Resources Retrieved": self.current_resources,
            "# of Fights": self.fights,
            "# of Escapes": self.escapes,
            "Murderer": self.murderer,
            "Alive": self.alive,
            "Mate": self.mate
        }

    def age_one_year(self):
        self.age += 1

    def move(self, direction):
        if direction == "N":
            self.position[0] += 1
        elif direction == "S":
            self.position[0] -= 1
        elif direction == "E":
            self.position[1] += 1
        else:  # W
            self.position[1] -= 1

    def sight(self, Grid):
        y_lim = 5
        x_lim = 5
        x_origin = 2
        y_origin = 2
        if (0 not in self.position and np.size(Grid[0]) - 1 not in self.position) and \
                (1 not in self.position and np.size(Grid[0]) - 2 not in self.position):
            pass
        else:
            if 0 == self.position[0]:  # Within 1 of Upper Wall
                y_origin = 0
                y_lim = 3
            elif 1 == self.position[0]:  # Within 2 of Upper Wall
                y_origin = 1
                y_lim = 4
            elif np.size(Grid[0]) - 1 == self.position[0]:  # Within 1 of Lower Wall
                y_lim = 3
            elif np.size(Grid[0]) - 2 == self.position[0]:  # Within 1 of Lower Wall
                y_lim = 4

            if 0 == self.position[1]:  # Within 1 of Left Wall
                x_origin = 0
                x_lim = 3
            elif 1 == self.position[1]:  # Within 2 of Left Wall
                x_origin = 1
                x_lim = 4
            elif np.size(Grid[0]) - 1 == self.position[1]:  # Within 1 of Right Wall
                x_lim = 3
            elif np.size(Grid[0]) - 2 == self.position[1]:  # Within 2 of Right Wall
                x_lim = 4

        return np.array([[Grid[self.position[0] - y_origin + i][self.position[1] - x_origin + j]
                          if (i != y_origin or j != x_origin) else "X" for j in range(x_lim)] for i in
                         range(y_lim)])

    def findObjectsInSight(self, Grid):
        def calcDistance(objectCoordinates):
            # Pythagoras's theorem return math.sqrt(((self.position[0] - objectCoordinates[0]) ** 2) + ((
            # self.position[1] - objectCoordinates[1]) ** 2))
            return [(2 - objectCoordinates[0]), (2 - objectCoordinates[1])]

        visGrid = self.sight(Grid)
        objectTypes = ['-1', '101', '1']
        objectTypeDict = {
            '-1': 'deadBody',
            '101': 'organism',
            '1': 'resource'
        }

        outList = []

        for objectType in objectTypes:
            # Is here, time to find
            for y, row in enumerate(visGrid):
                if objectType in row:
                    for x, element in enumerate(row):
                        if objectType == element:
                            outList.append([objectType, calcDistance([y, x])])

        return sorted([[objectTypeDict[n[0]], n[1], abs(n[1][0]) + abs(n[1][1])] for n in outList],
                      key=lambda ele: ele[2])

    def eat(self, Grid):
        pass

    def fight(self):
        pass

    def reproduce(self):
        pass

    def decide(self, Grid):
        def findDirection(coordinates):
            directionList = []
            if coordinates[0] > 0:
                directionList.append("N")
            elif coordinates[0] < 0:
                directionList.append("S")

            if coordinates[1] > 0:
                directionList.append("W")
            elif coordinates[1] < 0:
                directionList.append("E")

            return directionList

        if not self.alive:
            return

        objectsNearby = self.findObjectsInSight(Grid)
        # Simple Algo, act towards whatever is closest

        # decisionDict = {
        #     'deadBody': 8 - self.behavior,
        #     'organism': self.behavior,
        #     'resource': 8 - self.behavior
        # }

        if not objectsNearby:
            attemptingMove = True
            while attemptingMove:
                try:
                    self.move(sample(["N", "S", "W", "E"], 1)[0])  # Nothing nearby, move randomly
                    attemptingMove = False
                except:
                    pass
            return

        decision = objectsNearby[0]  # Closest object

        if 1 in decision[1]:  # check if any y or x direction is within 1 tile
            # Close enough to act
            # if decision[0] == 'deadBody':
            #     self.eat(Grid)
            pass  # Stop Moving
        else:
            attemptingMove = True
            while attemptingMove:
                try:
                    self.move(
                        sample(findDirection(decision[1]), 1)[0])  # pick random viable direction towards nearest object
                    attemptingMove = False
                except:
                    pass
