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
        y_temp = random.randint(0, len(grid) - 2)
        x_temp = random.randint(0, len(grid) - 2)
        if grid[y_temp][x_temp] == 0:  # Is Empty
            return [y_temp, x_temp]


def findNearestEmpty(grid, p1coors, p2coors):
    # search around parents
    for i in range(-1, 1):
        for j in range(-1, 1):
            if grid[p1coors[0] + i][p1coors[1] + j] == 0:
                if not any(x == -1 or x == len(grid) + 1 for x in [p1coors[0] + i, p1coors[1] + j]):
                    return [p1coors[0] + i, p1coors[1] + j]
            if grid[p2coors[0] + i][p2coors[1] + j] == 0:
                if not any(x == -1 or x == len(grid) + 1 for x in [p2coors[0] + i, p2coors[1] + j]):
                    return [p2coors[0] + i, p2coors[1] + j]


def gridToString(grid):
    def convertEntries(element):
        if str(type(element)) == "<class 'Organism.Organism'>":  # Is this an organism object?
            if element.alive:
                return 101
            elif element.corpse:
                return -1
        elif str(type(element)) == "<class '__main__.Resource'>":  # Is this a resource?
            return 1
        elif element == 'X':
            return 'X'
        return 0

    # draw temp version of this grid
    tempGrid = grid
    out_string = ''
    for y_array in tempGrid:
        out_string += ''.join(
            [str(convertEntries(x_elem)) + ' ' * (5 - len(str(convertEntries(x_elem)))) for x_elem in y_array])
        out_string += '\n'

    return out_string


class Organism:
    # Implement Binary Tree genealogy

    def __init__(self, parent1=None, parent2=None, first_gen=False, Env=None):
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

            if Env is None:
                self.position = [0, 0]  # y, x
            else:
                self.position = randomPosition(Env.grid.data)
            # Find the empty tile nearest both parents
        else:
            tempGenome = inherit(parent1.Genome, parent2.Genome, genome=True)  # function for inheritance
            tempMutation_Matrix = inherit(parent1.mutation_matrix, parent2.mutation_matrix)
            self.parent1id = parent1.id
            self.parent2id = parent2.id
            if Env is None:
                self.position = [0, 0]
            else:
                self.position = findNearestEmpty(Env.grid.data, parent1.position, parent2.position)
            # Find Random position on Grid

        self.last_position = [self.position[0], self.position[1]]

        self.mutation_matrix = mutate_matrix(tempMutation_Matrix)
        self.Genome = mutate_genome(tempGenome, self.mutation_matrix)

        # Initialize features / behaviors from Genome
        self.behavior, self.size, self.speed, self.vision = parseGenome(self.Genome)

        self.corpse = False

        # Check if Viable
        if "NonViable" in [self.behavior, self.size, self.speed]:
            self.death("NonViable")
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

    def death(self, murderer):
        self.alive = False
        self.murderer = murderer
        if random.randint(1, 10) > 9:
            # Make corpse
            self.corpse = True
        if murderer == "NonViable":
            self.viable = False

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

    def move_org(self, direction, Grid, reverse=1):
        self.last_position = [self.position[0], self.position[1]]
        # TODO: Add chance of moving twice based on speed stat
        if direction == "N":
            self.position[0] -= 1 * reverse
        elif direction == "S":
            self.position[0] += 1 * reverse
        elif direction == "E":
            self.position[1] += 1 * reverse
        else:  # W
            self.position[1] -= 1 * reverse
        if reverse == 1:
            print(f"Moving {direction}")
        else:
            reverseDict = {"W": "E", "N": "S", 'E': 'W', 'S': 'N'}
            print(f"Moving {reverseDict[direction]}")
        Grid.UpdatePosition(gridObject=self, oldCoordinates=self.last_position, newCoordinates=self.position)

    def sight(self, Grid):
        y_lim = 5
        x_lim = 5
        x_origin = 2
        y_origin = 2
        if (0 not in self.position and len(Grid[0]) - 1 not in self.position) and \
                (1 not in self.position and len(Grid[0]) - 2 not in self.position):
            pass
        else:
            if 0 == self.position[0]:  # Within 1 of Upper Wall
                y_origin = 0
                y_lim = 3
            elif 1 == self.position[0]:  # Within 2 of Upper Wall
                y_origin = 1
                y_lim = 4
            elif len(Grid[0]) - 1 == self.position[0]:  # Within 1 of Lower Wall
                y_lim = 3
            elif len(Grid[0]) - 2 == self.position[0]:  # Within 1 of Lower Wall
                y_lim = 4

            if 0 == self.position[1]:  # Within 1 of Left Wall
                x_origin = 0
                x_lim = 3
            elif 1 == self.position[1]:  # Within 2 of Left Wall
                x_origin = 1
                x_lim = 4
            elif len(Grid[0]) - 1 == self.position[1]:  # Within 1 of Right Wall
                x_lim = 3
            elif len(Grid[0]) - 2 == self.position[1]:  # Within 2 of Right Wall
                x_lim = 4

        return [[Grid[self.position[0] - y_origin + i][self.position[1] - x_origin + j]
                 if (i != y_origin or j != x_origin) else "X" for j in range(x_lim)] for i in
                range(y_lim)]

    def findObjectsInSight(self, Grid):
        def calcDistance(objectCoordinates, origin_coor):
            # Pythagoras's theorem return math.sqrt(((self.position[0] - objectCoordinates[0]) ** 2) + ((
            # self.position[1] - objectCoordinates[1]) ** 2))
            return [(origin_coor[0] - objectCoordinates[0]), (origin_coor[1] - objectCoordinates[1])]

        visGrid = self.sight(Grid)
        print(gridToString(visGrid))
        objectTypes = ["<class 'Organism.Organism'>", "<class '__main__.Resource'>", "<class 'int'>", "<class 'str'>"]
        objectTypeDict = {
            '-1': 'deadBody',
            '101': 'organism',
            '1': 'resource',
        }

        outList = []

        for y, row in enumerate(visGrid):
            if any([True if n in objectTypes else False for n in [str(type(x)) for x in row]]):
                for x, element in enumerate(row):
                    test_ele = str(type(element))
                    if test_ele in objectTypes:
                        if test_ele == "<class 'str'>":
                            o_coor = [y, x]
                        elif test_ele == "<class 'Organism.Organism'>":  # Check if org
                            if element.alive:
                                outList.append(['101', [y, x], element])
                            elif element.corpse:
                                outList.append(['-1', [y, x], element])
                        elif test_ele == "<class '__main__.Resource'>":  # Check if resource
                            outList.append(['1', [y, x], element])
        outList = [[n[0], calcDistance(n[1], o_coor), n[2]] for n in outList]

        return sorted([[objectTypeDict[n[0]], n[1], abs(n[1][0]) + abs(n[1][1]), n[2]] for n in outList],
                      key=lambda ele: ele[2])

    def eat(self, decision, Grid):
        # Decision[1] should contain the relative coordinates the object with which the organism is interacting
        if decision[0] == 'deadBody':
            print("Eating Dead Body")
            self.current_resources += 100  # Dead bodies equal to 2?
            # Consume the object
            decision[3].corpse = False
            Grid.drawFromDict(decision[3], empty=True)
        elif decision[0] == 'resource':
            print(f"Eating Resource")
            self.current_resources += 500  # Resources are more rewarding
            decision[3].consume(Grid)
        elif decision[0] == 'organism':
            self.fight(decision[3], Grid)

    def fight(self, opponent, Grid):
        print(f"{self.id} fighting {opponent.id}")
        # How should fighting work?
        offensive = random.randint(1, 10) + self.size
        defensive = random.randint(1, 10) + opponent.size

        # Victor takes some resources, dictated by the degree of victory
        # If the loser has no resources, they die and the victor gets extra
        if offensive > defensive:
            # Offense wins
            winner = self
            loser = opponent
        else:  # defense wins ties
            winner = opponent
            loser = self

        tracker = 0

        # Check loser's resources
        if loser.current_resources > 0:
            # take away 400, 1 at a time and give triple that to the victor with a minimum of 800
            counter = 400
            while loser.current_resources > 0 and counter > 0:
                winner.current_resources += 3
                tracker += 3
                loser.current_resources -= 1
                counter -= 1

        if tracker < 800:
            winner.current_resources += 800 - tracker

        # If loser has been drained, kill them
        if loser.current_resources <= 0:
            loser.death(winner)
            Grid.drawFromDict(loser, empty=True)

    def reproduce(self):
        pass  # TODO: When and how reproduction works

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

        print(f"{self.id} at position {self.position} making a decision.")

        objectsNearby = self.findObjectsInSight(Grid.data)
        # Simple Algo, act towards whatever is closest
        print(f"Nearby Objects: {objectsNearby}")

        # decisionDict = {
        #     'deadBody': 8 - self.behavior,
        #     'organism': self.behavior,
        #     'resource': 8 - self.behavior
        # }

        if not objectsNearby:  ## These movements are repetitive, could be improved
            print("Attempting Random Move, nothing nearby.")
            attemptingMove = True
            while attemptingMove:
                try:
                    dir_list = ["N", "S", "W", "E"]
                    if self.position[0] == 0:  # Can't go North
                        dir_list.pop(dir_list.index('N'))
                    elif self.position[0] == Grid.dim - 1:  # Can't go South
                        dir_list.pop(dir_list.index('S'))

                    if self.position[1] == 0:  # Can't go West
                        dir_list.pop(dir_list.index('W'))
                    elif self.position[1] == Grid.dim - 1:  # Can't go East
                        dir_list.pop(dir_list.index('E'))

                    self.move_org(sample(dir_list, 1)[0], Grid)  # Nothing nearby, move randomly
                    attemptingMove = False
                except:
                    pass
            return

        decision = objectsNearby[0]  # Closest object

        if 1 == decision[2]:  # check if any y or x direction is within 1 tile
            print(f"Close enough to {decision}")
            # Close enough to act
            if decision[0] in ['deadBody', 'resource']:
                self.eat(decision, Grid)
            elif decision[0] == 'organism':
                # Fight or Flight
                roll = random.randint(1, 8)
                if roll < self.behavior:
                    self.eat(decision, Grid)
                else:
                    attemptingMove = True
                    print(f"Moving Away From {decision}")
                    fail_safe = 0
                    while attemptingMove:
                        try:
                            print("Moving Away")
                            dir_list = findDirection(decision[1])
                            alt_list = ["N", "S", "W", "E"]
                            if self.position[0] == 0:  # Can't go North
                                if "N" in dir_list:
                                    dir_list.pop(dir_list.index('N'))
                                alt_list.pop(alt_list.index('N'))
                            elif self.position[0] == Grid.dim - 1:  # Can't go South
                                if "S" in dir_list:
                                    dir_list.pop(dir_list.index('S'))
                                alt_list.pop(alt_list.index('S'))
                            if self.position[1] == 0:  # Can't go West
                                if "W" in dir_list:
                                    dir_list.pop(dir_list.index('W'))
                                alt_list.pop(alt_list.index('W'))
                            elif self.position[1] == Grid.dim - 1:  # Can't go East
                                if "E" in dir_list:
                                    dir_list.pop(dir_list.index('E'))
                                alt_list.pop(alt_list.index('E'))

                            if len(dir_list) == 0: # TODO: Do not like this, needs to be fixed later
                                print('No desirable Valid Moves, making a random valid Move')
                                dir_list = alt_list

                            if len(dir_list) == 0:
                                print('No valid moves, must fight')
                                self.eat(decision, Grid)
                                attemptingMove = False

                            fail_safe += 1
                            if fail_safe > 5:
                                break
                                exit(0)

                            self.move_org(
                                sample(dir_list, 1)[0],
                                Grid, reverse=-1)  # pick random viable direction towards nearest object
                            attemptingMove = False
                        except:
                            pass

        else:
            attemptingMove = True
            print(f"Moving towards {decision}")
            while attemptingMove:
                try:
                    print("Moving Towards")
                    dir_list = findDirection(decision[1])
                    alt_list = ["N", "S", "W", "E"]
                    if self.position[0] == 0:  # Can't go North
                        if "N" in dir_list:
                            dir_list.pop(dir_list.index('N'))
                        alt_list.pop(alt_list.index('N'))
                    elif self.position[0] == Grid.dim - 1:  # Can't go South
                        if "S" in dir_list:
                            dir_list.pop(dir_list.index('S'))
                        alt_list.pop(alt_list.index('S'))
                    if self.position[1] == 0:  # Can't go West
                        if "W" in dir_list:
                            dir_list.pop(dir_list.index('W'))
                        alt_list.pop(alt_list.index('W'))
                    elif self.position[1] == Grid.dim - 1:  # Can't go East
                        if "E" in dir_list:
                            dir_list.pop(dir_list.index('E'))
                        alt_list.pop(alt_list.index('E'))

                    if len(dir_list) == 0:  # TODO: Do not like this, needs to be fixed later
                        print('No desirable Valid Moves, making a random valid Move')
                        dir_list = alt_list

                    if len(dir_list) == 0:
                        print('No valid moves, must fight')
                        self.eat(decision, Grid)
                        attemptingMove = False

                    self.move_org(
                        sample(dir_list, 1)[0],
                        Grid)  # pick random viable direction towards nearest object
                    attemptingMove = False
                except:
                    pass
