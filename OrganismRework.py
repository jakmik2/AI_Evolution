import random
from random import sample
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

# Build out using Numpy Arrays

# Globals
World = np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8,
                   9, 10, 11, 12, 13, 14, 15]],
                 dtype=object)

"""
Construction of each Array in NP Array:
[0 Unique Index, 1 Age, 2 Genome, 3 Mutation Matrix, 4 Parent 1 ID, 5 Parent 2 ID, 6 Behavior, 7 Size, 8 Speed, 
9 Resource Demand, 10 Current Resources, 11 Fights, 12 Escapes, 13 Murderer, 14 Alive,  15 Mate]
"""


def mutate_matrix(mutation_matrix):
    for i in range(len(mutation_matrix)):
        localRandomValue = random.randint(0, 5)
        localRandomValue = localRandomValue / 100
        coin_flip = random.randint(0, 100)
        if coin_flip > 50:
            mutation_matrix[i] = mutation_matrix[i] + localRandomValue
        else:
            mutation_matrix[i] = mutation_matrix[i] - localRandomValue
    return mutation_matrix


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


def parseGenome(genome):
    # Behavior: Hostile / Timid
    behavior_dict = {
        "AT": "Hostile",
        "AC": "Hostile",
        "CA": "Hostile",
        "TA": "Hostile",
        "AA": "Hostile",
        "GG": "Hostile",
        "GT": "Timid",
        "GC": "Timid",
        "CG": "Timid",
        "TC": "Timid",
        "TT": "Timid",
        "CC": "Hostile",
        "AG": "Hostile",
        "GA": "Timid",
        "CT": "Timid",
        "TG": "NonViable"
    }
    # Size: Large / Medium / Small
    size_dict = {
        "AT": "Large",
        "AC": "Medium",
        "CA": "Small",
        "TA": "Medium",
        "GT": "Large",
        "GC": "Medium",
        "CG": "Small",
        "TC": "Medium",
        "AG": "Large",
        "GA": "Medium",
        "CT": "Small",
        "TG": "Medium",
        "AA": "Large",
        "TT": "Medium",
        "CC": "Small",
        "GG": "NonViable"
    }

    # Speed: Fast / Average / Slow
    speed_dict = {
        "AT": "Fast",
        "AC": "Fast",
        "CA": "NonViable",
        "TA": "Average",
        "GT": "Average",
        "GC": "Slow",
        "CG": "Average",
        "TC": "Average",
        "AG": "Average",
        "GA": "Slow",
        "CT": "Slow",
        "TG": "Average",
        "AA": "Fast",
        "TT": "Average",
        "GG": "Slow",
        "CC": "Average"
    }
    output_list = []

    # Check Valid Primer
    if genome[:3] == "ATC":
        # Valid
        # Evaluate Behavior
        output_list.append(behavior_dict[genome[4:6]])
        # Evaluate Size
        output_list.append(size_dict[genome[7:9]])
        # Evaluate Speed
        output_list.append(speed_dict[genome[10:12]])
    else:
        output_list = ["NonViable" for x in range(3)]

    return output_list


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


def newOrg(p1index="", p2index=""):
    global World

    # Inherit or Initialize
    if p1index == "" or p2index == "":
        genome = "ATCCATGCGTGACTA"
        mm = [0.5 for r in range(14)]
        parent1 = ""
        parent2 = ""
    else:
        mm = inherit(World[p1index][3], World[p2index][3])
        genome = inherit(World[p1index][2], World[p2index][2], genome=True)
        parent1 = World[p1index][0]
        parent2 = World[p2index][0]

    # Mutate Values
    mm = mutate_matrix(mm)
    genome = mutate_genome(genome, mm)

    # Interpret Genome
    features = parseGenome(genome)
    resources_required = 6
    if features[1] == "Large":
        resources_required += 1
    if features[1] == "Small":
        resources_required -= 1
    if features[2] == "Fast":
        resources_required += 1
    if features[2] == "Slow":
        resources_required -= 2

    # Add the new organism
    World = np.append(World, [[World.size / 16, 0, genome, mm, parent1, parent2, features[0], features[1], features[2],
                               resources_required, 0, 0, 0, None, not any([n == "NonViable" for n in features]), None]],
                      axis=0)


"""
Construction of each Array in NP Array:
[0 Unique Index, 1 Age, 2 Genome, 3 Mutation Matrix, 4 Parent 1 ID, 5 Parent 2 ID, 6 Behavior, 7 Size, 8 Speed, 
9 Resource Demand, 10 Current Resources, 11 Fights, 12 Escapes, 13 Murderer, 14 Alive,  15 Mate]
"""


def super_func(function, index):
    global World

    World[:, index] = np.apply_along_axis(function, 1, World)


def get_total_pop():
    global World

    return int(World.size // 16) - 1


def get_total_alive():
    global World

    return len([n for n in World[:, 14] if n == True])


def forage():
    super_func(forage_sp, 10)


def forage_sp(a):
    total_pop = get_total_pop()
    total_alive = get_total_alive()

    if a[6] == "Timid" and a[14] == True:
        print('in')
        odds = 0
        if a[8] == "Fast":
            odds += 1
        if a[7] == "Slow":
            odds -= 1

        ForageAmt = random.randint(1, 3)
        ForageAmt = ForageAmt * total_pop / total_alive
        org_roll = random.randint(1, 6) + odds

        if org_roll <= 1:
            foraged = 0
        elif org_roll < 3:
            foraged = ForageAmt / 2
        elif org_roll >= 3:
            foraged = ForageAmt
        return a[10] + foraged
    else:
        return int(a[10])
    

if __name__ == '__main__':
    # Create 12 organisms
    print(World)
    for i in range(50):
        newOrg()

    print(World)

    forage()

    print(World)
