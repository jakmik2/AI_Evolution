import os
import time
import random
from random import sample
import pandas as pd
import numpy as np
from timeit import default_timer as timer
import math
import numba
from numba import jit


pd.set_option('display.max_columns', None)

# Build out using Numpy Arrays


"""
Construction of each Array in NP Array:
[0 Unique Index, 1 Age, 2 Genome, 3 Mutation Matrix, 4 Parent 1 ID, 5 Parent 2 ID, 6 Behavior, 7 Size, 8 Speed, 
9 Resource Demand, 10 Current Resources, 11 Fights, 12 Escapes, 13 Murderer, 14 Alive,  15 Mate 16]
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


def newOrg(p1index="", p2index="", firstOrg=False):
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
    if firstOrg:
        World = np.array([[0, 0, genome, mm, parent1, parent2, features[0], features[1], features[2], resources_required,
                           0, 0, 0, None, not any([n == "NonViable" for n in features]), "None", None]])

    World = np.append(World, [[World[np.size(World, 0)-1][0]+1, 0, genome, mm, parent1, parent2, features[0], features[1], features[2],
                               resources_required, 0, 0, 0, None, not any([n == "NonViable" for n in features]), "None",
                               None]],
                      axis=0)


"""
Construction of each Array in NP Array:
[0 Unique Index, 1 Age, 2 Genome, 3 Mutation Matrix, 4 Parent 1 ID, 5 Parent 2 ID, 6 Behavior, 7 Size, 8 Speed, 
9 Resource Demand, 10 Current Resources, 11 Fights, 12 Escapes, 13 Murderer, 14 Alive,  15 Mate, 16 TAG]
"""


## Could this be a property of data type 'World'?
def super_func(function, index, key=None):
    global World
    if key is not None:
        World[:, index] = np.apply_along_axis(function, 1, World, key)
    else:
        World[:, index] = np.apply_along_axis(function, 1, World)


## Could this be a propery of data type 'World'?
def get_total_pop():
    global World

    return int(np.size(World, 0)) - 1


## Could this be a propery of data type 'World'?
def get_total_alive():
    global World

    return len([n for n in World[:, 14] if n == True])


def forage():
    global initialPop

    def forage_sp(a):
        total_alive = get_total_alive()

        if a[6] == "Timid" and a[14] == True:
            odds = 0
            if a[8] == "Fast":
                odds += 1
            if a[7] == "Slow":
                odds -= 1

            ForageAmt = random.randint(1, 3)
            ForageAmt = ForageAmt * initialPop / total_alive
            org_roll = random.randint(1, 6) + odds

            if org_roll <= 1:
                foraged = 0
            elif org_roll < 3:
                foraged = ForageAmt / 2
            elif org_roll >= 3:
                foraged = ForageAmt
            return a[10] + foraged
        else:
            return a[10]

    super_func(forage_sp, 10)


def starvation():
    # I don't like this, would rather fix this up to not have to double call super_func
    def starvation_sp1(a):
        if a[6] == 6:
            return True
        elif a[10] <= a[9] and a[14] == True:
            a[13] = 'Starvation'
            return False  # Alive
        else:
            return a[14]

    super_func(starvation_sp1, 14)


def hunt():
    global World

    def hunt_sp(a):
        if a[6] == 6:
            return a[10]
        if a[6] == "Hostile" and a[14] == True:
            hunting = True
            while hunting:
                if get_total_alive() < 2:
                    hunting = False
                randomPick = sample(range(get_total_pop()), 1)
                rand_Org = World[randomPick[0]]

                if rand_Org[0] != a[0] and rand_Org[14] == True:
                    # Determine Fight Score
                    fighters = [6, 6]
                    for index, org in enumerate([a, rand_Org]):
                        if org[7] == "Large":
                            fighters[index] += 1
                        if org[7] == "Small":
                            fighters[index] -= 1
                        if org[8] == "Fast":
                            fighters[index] += 1
                        if org[8] == "Slow":
                            fighters[index] -= 1

                    # Roll
                    org1_roll = random.randint(1, fighters[0])
                    org2_roll = random.randint(1, fighters[1])

                    caught = False

                    if org1_roll > org2_roll:
                        # Return an array of Trues and False
                        caught = True
                    else:
                        hunting = False
                    # Add Fights
            World[a[0]][11] += 1
            World[rand_Org[0]][11] += 1

            # Check if Caught
            if caught:
                # Murder
                World[rand_Org[0]][14] = False
                World[rand_Org[0]][13] = a[0]

                resources_earned = a[10] + 4 * (initialPop / get_total_alive()) + World[rand_Org[0]][10]
            else:
                # Escape
                World[rand_Org[0]][12] += 1

                resources_earned = a[10]
            return resources_earned
        else:
            return a[10]

    super_func(hunt_sp, 10)


def reproduce():
    global World

    def repro_sp1(a): # Returns MATE column
        global World

        if a[6] == 6:
            return 0
        elif a[14] == True and a[10] >= a[9]:
            if get_total_alive() < 2:
                return 'Parthenogenesis'
            #Find viable mate
            while True:
                randomPick = sample(range(get_total_pop()), 1)
                rand_Org = World[randomPick[0]]

                if rand_Org[0] != a[0] and rand_Org[14] == True:
                    if a[10] // 2 > a[9]:
                        a[16] = "Double Reproduction"
                    return rand_Org[0]
        return 0

    def repro_sp2(a): # Acts on MATE column
        global World

        if a[6] == 6:
            return a[16]
        elif a[15] != 0:
            if a[15] == 'Parthenogenesis':
                p2 = a[0]
                fornicate = True
            else:
                p2 = a[15]
                fornicate = True

            dblrep = 1

            if a[16] == "Double Reproduction":
                dblrep = 2

            if fornicate:
                for nums in range(dblrep):
                    for j in range(3):
                        newOrg(a[0], p2)

            a[16] = 'None'
        return 0

    super_func(repro_sp1, 15)
    np.apply_along_axis(repro_sp2, 1, World)


def purgeDead():
    global World
    global newIndex

    newIndex = -1

    def purge_sp1(a):
        global newIndex

        newIndex += 1
        return newIndex

    World = np.array([array for array in World if array[14] == True])

    super_func(purge_sp1, 0)

def reset():
    global World

    def reset_res_sp(a):
        return 0

    super_func(reset_res_sp, 10)


def liveYears(n_years = 1):
    # os.mkdir(f'{n_years}')
    timeArray = []
    for year in range(n_years):
        print(f'--------------------YEAR {year} ------------------')
        startTime = timer()
        totAl = get_total_alive()
        forage()
        hunt()
        forage()
        hunt()
        starvation()
        reproduce()
        df = pd.DataFrame(World)
        # df.to_csv(f'{n_years}//{year}_dataframe.csv')
        purgeDead()
        reset()
        endTime = timer()
        timeArray.append((endTime-startTime)/totAl)


    return timeArray

if __name__ == '__main__':
    global initialPop
    start = timer()
    # Create 12 organisms
    newOrg(firstOrg=True)
    for i in range(999):
        newOrg()

    initialPop = get_total_pop()

    timeArr = liveYears(50)
    end = timer()
    print(end - start)
    print("Average: ", sum(timeArr)/len(timeArr))
    print("Longest: ", max(timeArr))
    print("Quickest: ", min(timeArr))



