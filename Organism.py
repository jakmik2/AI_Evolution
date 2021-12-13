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
counter = 10000
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
    else:
        output_list = ["NonViable" for x in range(3)]

    if any(["NonViable" for x in output_list if x == 0.5 or x == 8]):
        output_list = ["NonViable" for x in range(3)]

    return output_list


def randomPosition(grid):
    notFound = True
    while notFound:
        y_temp = random.randint(0, np.size(grid[0])-1)
        x_temp = random.randint(0, np.size(grid[0])-1)
        if grid[y_temp][x_temp] == 0:
            return [y_temp, x_temp]


def findNearestEmpty(grid, p1coors, p2coors):
    # search around parents
    for i in range(-1, 1):
        for j in range(-1, 1):
            if grid[p1coors[0]+i][p1coors[1]+j] == 0:
                if not any(x == -1 or x == np.size(grid) + 1 for x in [p1coors[0]+i, p1coors[1]+j]):
                    return [p1coors[0]+i, p1coors[1]+j]
            if grid[p2coors[0]+i][p2coors[1]+j] == 0:
                if not any(x == -1 or x == np.size(grid) + 1 for x in [p2coors[0]+i, p2coors[1]+j]):
                    return [p2coors[0]+i, p2coors[1]+j]


class Organism:
    # Implement Binary Tree genealogy

    def __init__(self, parent1=None, parent2=None, first_gen=False, Grid=None):
        global counter
        global current_year
        # Self Initialization
        # Inherit Mutation Matrix
        # Then mutate their genome
        if first_gen:
            tempGenome = "ATCTGTTGGTGATGA"
            tempMutation_Matrix = [0.5 for r in range(14)]
            self.parent1id = parent1
            self.parent2id = parent2

            if Grid is None:
                self.position = [0, 0] # y, x
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


class OrganismList:
    global total_pop

    def __init__(self, list_of_organisms):
        self.organisms = list_of_organisms

    def total_alive(self):
        return len([n for n in self.organisms if n.alive == True])

    def total_dead(self):
        return len([n for n in self.organisms if n.alive == False])

    def purge_dead(self):
        self.organisms = [n for n in self.organisms if n.alive == True]

    def feed(self):
        [self.forage_subprocess(n) for n in self.organisms]
        [self.hunt_subprocess(n) for n in self.organisms]

    def forage_subprocess(self, org):
        if org.alive:
            odds = 0
            odds += org.size / 2 - 3
            odds += org.speed / 2 - 3

            # Random Forage Amount
            ForageAmt = random.randint(1, 3)
            # Reward of this activity equal proportionate to specialization of this activity
            ForageAmt = ForageAmt * 12 * (total_pop // self.total_alive()) * (8 - org.behavior)
            org_roll = random.randint(1, 6) + odds

            # Evaluate Roll
            if org_roll <= 1:
                foraged = 0
            elif org_roll < 3:
                foraged = ForageAmt // 2
            elif org_roll >= 3:
                foraged = ForageAmt

            org.current_resources += foraged

    def hunt_subprocess(self, org):
        # Roll to check if fight
        if org.alive:
            have_not_fought = True
            while have_not_fought:
                if self.total_alive() < 2:
                    have_not_fought = False
                randomPick = sample(range(len(self.organisms)), 1)
                rand_Org = self.organisms[randomPick[0]]

                if rand_Org.id != org.id and rand_Org.alive == True:
                    self.org_fight(org, rand_Org)
                    have_not_fought = False

    def org_fight(self, org1, org2):
        # Determine Fight Score
        # Try and catch
        org1_dex_check = random.randint(1, 10) + org1.speed
        org2_dex_check = random.randint(1, 10) + org2.speed
        if org1_dex_check > org2_dex_check:
            # Caught
            # Attempt Fight
            org1_fight_roll = random.randint(1, 10) + org1.size
            org2_fight_roll = random.randint(1, 10) + org2.size

            if org1_fight_roll > org2_fight_roll:
                # Org 1 Wins
                print(f"{org1.id} ate {org2.id}")
                org2.alive = False
                org1.current_resources += (25 * (total_pop // self.total_alive()) + org2.current_resources) * org1.behavior

        org1.fights += 1
        org2.fights += 1

    def starved_super(self):
        [self.starved_subprocess(n) for n in self.organisms]

    # @staticmethod
    def starved_subprocess(self, org):
        if org.current_resources < org.resource_demand:
            org.alive = False
            org.murderer = "Starvation"

    def reproduce_super(self):
        [n.age_one_year() for n in self.organisms]
        [self.reproduce_subprocess(n) for n in self.organisms]
        [n.reset_resources() for n in self.organisms]

    def reproduce_subprocess(self, org):
        if org.alive == True and org.current_resources >= org.resource_demand:
            print(f'{org.id} attempting reproduction')
            have_not_reproduced = True
            second_reproduction = False
            while have_not_reproduced:
                if self.total_alive() < 2:
                    print("Parthenogenesis!")
                    # Increase mutation at every node
                    org.mutation_matrix = [x - 0.05 for x in org.mutation_matrix]
                    # Reproduce 5 Times
                    self.organisms.append(Organism(org, org))
                    self.organisms.append(Organism(org, org))
                    self.organisms.append(Organism(org, org))
                    self.organisms.append(Organism(org, org))
                    self.organisms.append(Organism(org, org))
                randomPick = sample(range(len(self.organisms)), 1)
                rand_Org = self.organisms[randomPick[0]]
                if rand_Org.id != org.id and rand_Org.alive == True:
                    self.organisms.append(Organism(org, rand_Org))
                    self.organisms.append(Organism(org, rand_Org))
                    self.organisms.append(Organism(org, rand_Org))
                    org.mate = rand_Org.id
                    rand_Org.mate = org.id
                    if org.current_resources / 2 >= org.resource_demand and second_reproduction == False:
                        second_reproduction = True
                    else:
                        second_reproduction = False

                    if not second_reproduction:
                        have_not_reproduced = False


def year(Orgs, n_years=1, beginning_year=0):
    global current_year
    current_year = beginning_year
    # os.mkdir('original')
    outArray = []
    for i in range(n_years):
        start = timer()

        print(f'--------------------YEAR {i} ------------------')
        # plentiful (How many resources happen to be available this generation
        living = Orgs.total_alive()
        plentiful = random.randint(0, 3)
        [n.add_resources(plentiful) for n in Orgs.organisms]
        print(Orgs.total_alive())
        # Forage
        Orgs.feed()
        Orgs.feed()

        # print(f"{Orgs.total_alive()} are alive currently")

        # df = pd.DataFrame.from_records([org.to_dict() for org in Orgs.organisms])

        # df.to_csv(f"original//{i}_year_10K.csv")
        current_year += 1

        # Reproduce and Age
        Orgs.reproduce_super()

        Orgs.purge_dead()
        end = timer()

        outArray.append((end - start) / living)

    return outArray


if __name__ == '__main__':
    start = timer()
    # Create 12 organisms
    organisms = []
    total_pop = 1000
    for i in range(total_pop):
        organisms.append(Organism(first_gen=True))

    Orgs = OrganismList(organisms)

    print(Orgs.organisms[0].to_dict())
    n_years = 500
    timeArr = year(Orgs, n_years, current_year)
    end = timer()

    print(end - start)

    print("Average: ", sum(timeArr) / len(timeArr))
    print("Longest: ", max(timeArr))
    print("Quickest: ", min(timeArr))
