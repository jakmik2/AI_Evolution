import os
import numpy
import pandas as pd
import random
from random import sample

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
counter = 100000
current_year = 0
total_pop = 1000


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
    for i, ele in enumerate(mutation_matrix):
        randInt = random.randint(0, 20)
        if randInt > 20 * ele:
            out_genome += bases[int(randInt % 4)]
        else:
            out_genome += genome[i]
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


class Organism:
    # Implement Binary Tree genealogy

    def __init__(self, parent1=None, parent2=None, first_gen=False):
        global counter
        global current_year
        # Self Initialization
        # Inherit Mutation Matrix
        # Then mutate their genome
        if first_gen:
            tempGenome = "ATCCATGCGTGACTA"
            tempMutation_Matrix = [0.5 for r in range(14)]
            self.parent1id = parent1
            self.parent2id = parent2
        else:
            tempGenome = inherit(parent1.Genome, parent2.Genome, genome=True)  # function for inheritance
            tempMutation_Matrix = inherit(parent1.mutation_matrix, parent2.mutation_matrix)
            self.parent1id = parent1.id
            self.parent2id = parent2.id

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
        else:
            self.viable = True
            self.alive = True
            self.murderer = None

        # Evaluate Resource Requirements
        resources_required = 6
        if self.size == "Large":
            resources_required += 1
        if self.size == "Small":
            resources_required -= 1
        if self.speed == "Fast":
            resources_required += 1
        if self.speed == "Slow":
            resources_required -= 2

        self.resource_demand = resources_required
        self.current_resources = 0
        self.fights = 0
        self.escapes = 0
        self.id = counter + 1
        self.mate = None
        self.birthyear = current_year
        self.age = 0

        counter += 1

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
    def __init__(self, list_of_organisms):
        self.organisms = list_of_organisms

    def total_alive(self):
        return len([n for n in self.organisms if n.alive == True])

    def total_dead(self):
        return len([n for n in self.organisms if n.alive == False])


# TODO: REFACTOR
def organism_fight(org1, org2, Orgs):
    global total_pop
    print("-------FIGHT-------")
    print(org1.id)
    print(org1.behavior)
    print(org1.size)
    print(org1.speed)
    print(org2.id)
    print(org2.behavior)
    print(org2.size)
    print(org2.speed)
    # Determine Fight Score
    orgs = [org1, org2]
    fighters = [6, 6]
    for index in range(len(orgs)):
        org = orgs[index]
        if org.size == "Large":
            fighters[index] += 1
        if org.size == "Small":
            fighters[index] -= 1
        if org.speed == "Fast":
            fighters[index] += 1
        if org.speed == "Slow":
            fighters[index] -= 1

    # Roll
    org1_roll = random.randint(1, fighters[0])
    org2_roll = random.randint(1, fighters[1])

    if org1_roll > org2_roll:
        print(org2.id, " Dies")
        org2.alive = False
        org1.current_resources += 4 * (total_pop/Orgs.total_alive()) + org2.current_resources
    elif org2_roll >= org1_roll:
        print(org2.id, " escapes!")

    org1.fights += 1
    org2.fights += 1


def Foraging(org, Orgs):
    global total_pop
    if org.behavior == "Timid" and org.alive == True:
        print(org.id, " is foraging!")
        odds = 0
        if org.speed == "Fast":
            odds += 1
        if org.speed == "Slow":
            odds -= 1

        # Random Forage Amount
        ForageAmt = random.randint(2, 3)
        ForageAmt = ForageAmt * (total_pop/Orgs.total_alive())
        org_roll = random.randint(1, 6) + odds

        # Evaluate Roll
        if org_roll <= 1:
            foraged = 0
        elif org_roll < 3:
            foraged = ForageAmt / 2
        elif org_roll >= 3:
            foraged = ForageAmt

        org.current_resources += ForageAmt


def reproduce(org_list):
    out_list = []
    for org in org_list:
        if org.alive == True and org.current_resources >= org.resource_demand:
            print("attempting repro")
            have_not_reproduced = True
            second_reproduction = False
            while have_not_reproduced:
                if len(org_list) <= 1:
                    print("No one to reproduce with, fatal for all")
                    have_not_reproduced = False
                randomPick = sample(range(len(org_list)), 1)
                rand_Org = org_list[randomPick[0]]
                if rand_Org.id != org.id and rand_Org.alive == True:
                    print(f"{org.id} is mating with {rand_Org.id}")
                    out_list.append(Organism(org, rand_Org))
                    out_list.append(Organism(org, rand_Org))
                    out_list.append(Organism(org, rand_Org))
                    org.mate = rand_Org.id
                    rand_Org.mate = org.id
                    if org.current_resources / 2 >= org.resource_demand and second_reproduction == False:
                        second_reproduction = True
                    else:
                        second_reproduction = False

                    if not second_reproduction:
                        have_not_reproduced = False

    return out_list


def year(Orgs, n_years=1, beginning_year=0):
    global current_year
    current_year = beginning_year
    for i in range(n_years):
        organisms = Orgs.organisms
        # plentiful (How many resources happen to be available this generation
        plentiful = random.randint(0, 3)

        # All Hostile Creatures Must Fight
        for org in organisms:
            org.current_resources += plentiful  # All organisms benefit from nature's bounty
            if org.behavior == "Hostile" and org.alive == True:
                fight = False
                have_not_fought = True
                while have_not_fought:
                    if len(organisms) <= 2:
                        print("No one to fight.")
                        have_not_fought = False
                    randomPick = sample(range(len(organisms)), 1)
                    rand_Org = organisms[randomPick[0]]
                    if rand_Org.id != org.id and rand_Org.alive == True:
                        if rand_Org.behavior == "Timid":
                            luck_roll = random.randint(1, 20)
                            if luck_roll < 10:
                                fight = True
                        else:
                            fight = True
                        if fight:
                            organism_fight(org, rand_Org, Orgs)
                            have_not_fought = False

        print("Remaining After Hunt", Orgs.total_alive())

        # Foraging
        for org in organisms:
            Foraging(org, Orgs)

        # All Hostile Creatures Must Fight
        for org in organisms:
            org.current_resources += plentiful  # All organisms benefit from nature's bounty
            if org.behavior == "Hostile" and org.alive == True:
                fight = False
                have_not_fought = True
                while have_not_fought:
                    if len(organisms) <= 2:
                        print("No one to fight.")
                        have_not_fought = False
                    randomPick = sample(range(len(organisms)), 1)
                    rand_Org = organisms[randomPick[0]]
                    if rand_Org.id != org.id and rand_Org.alive == True:
                        if rand_Org.behavior == "Timid":
                            luck_roll = random.randint(1, 20)
                            if luck_roll < 10:
                                fight = True
                        else:
                            fight = True
                        if fight:
                            organism_fight(org, rand_Org, Orgs)
                            have_not_fought = False

        print("Remaining After Second Hunt", len(organisms))

        # Foraging
        for org in organisms:
            Foraging(org, Orgs)
            if org.current_resources < org.resource_demand * 0.75 and org.alive == True:
                print(org.id, "did not get enough to eat.")
                print(f"{org.id} got {org.current_resources}/{org.resource_demand}")
                org.alive = False
                org.murderer = "Starvation"

        print(f"-----------ENDING YEAR {i}-----------")

        df = pd.DataFrame.from_records([org.to_dict() for org in organisms])

        df.to_csv(f"{i}_year_10K.csv")
        current_year += 1

        children = reproduce(organisms)

        for org in organisms:
            org.age_one_year()
            org.reset_resources()

        Orgs.organisms += children




if __name__ == '__main__':
    # Create 12 organisms
    organisms = []
    for i in range(1000):
        organisms.append(Organism(first_gen=True))

    Orgs = OrganismList(organisms)
    year(Orgs, 150, current_year)
