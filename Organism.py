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
total_pop = 400  # Max Environment can handle


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

    def the_forage_super(self):
        print("Foraging!")
        [self.forage_subprocess(n) for n in self.organisms]

    def forage_subprocess(self, org):
        if org.behavior == "Timid" and org.alive == True:
            odds = 0
            if org.speed == "Fast":
                odds += 1
            if org.speed == "Slow":
                odds -= 1

            # Random Forage Amount
            ForageAmt = random.randint(1, 3)
            ForageAmt = ForageAmt * (total_pop / self.total_alive())
            org_roll = random.randint(1, 6) + odds

            # Evaluate Roll
            if org_roll <= 1:
                foraged = 0
            elif org_roll < 3:
                foraged = ForageAmt / 2
            elif org_roll >= 3:
                foraged = ForageAmt

            org.current_resources += foraged

    def starved_super(self):
        [self.starved_subprocess(n) for n in self.organisms]

    @staticmethod
    def starved_subprocess(org):
        if org.current_resources < org.resource.demand:
            org.alive = False
            org.murderer = "Starvation"

    def the_hunt_super(self):
        print("Hunting!")
        [self.hunt_subprocess(n) for n in self.organisms]

    def hunt_subprocess(self, org):
        if org.behavior == "Hostile" and org.alive == True:
            have_not_fought = True
            while have_not_fought:
                if self.total_alive() < 2:
                    print("No one to fight.")
                    have_not_fought = False
                randomPick = sample(range(len(self.organisms)), 1)
                rand_Org = self.organisms[randomPick[0]]

                if rand_Org.id != org.id and rand_Org.alive == True:
                    self.org_fight(org, rand_Org)
                    have_not_fought = False

    def org_fight(self, org1, org2):
        # Determine Fight Score
        fighters = [6, 6]
        for index, org in enumerate([org1, org2]):
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
            org2.alive = False
            org1.current_resources += 4 * (total_pop / self.total_alive()) + org2.current_resources

        org1.fights += 1
        org2.fights += 1

    def reproduce_super(self):
        print("Reproducing")
        [n.age_one_year() for n in self.organisms]
        [self.reproduce_subprocess(n) for n in self.organisms]
        [n.reset_resources() for n in self.organisms]

    def reproduce_subprocess(self, org):
        if org.alive == True and org.current_resources >= org.resource_demand:
            have_not_reproduced = True
            second_reproduction = False
            while have_not_reproduced:
                if self.total_alive() <= 1:
                    print("No one to reproduce with, fatal for all")
                    have_not_reproduced = False
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
    for i in range(n_years):
        # plentiful (How many resources happen to be available this generation
        print(i)
        plentiful = random.randint(0, 3)
        [n.add_resources(plentiful) for n in Orgs.organisms]
        print(f"{Orgs.total_alive()} are alive currently")

        # Forage
        Orgs.the_forage_super()

        # All Hostile Creatures Must Fight
        # Orgs.the_hunt_super()
        # print(f"{Orgs.total_alive()} are alive currently")

        # Forage
        Orgs.the_forage_super()

        # Hunt
        Orgs.the_hunt_super()
        print(f"{Orgs.total_alive()} are alive currently")

        df = pd.DataFrame.from_records([org.to_dict() for org in Orgs.organisms])

        df.to_csv(f"{i}_year_10K.csv")
        current_year += 1

        # Reproduce and Age
        Orgs.reproduce_super()

        Orgs.purge_dead()


if __name__ == '__main__':
    # Create 12 organisms
    organisms = []
    for i in range(400):
        organisms.append(Organism(first_gen=True))

    Orgs = OrganismList(organisms)
    n_years = 50
    year(Orgs, n_years, current_year)
