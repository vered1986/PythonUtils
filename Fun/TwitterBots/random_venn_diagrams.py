import os
import time
import json
import tweepy
import random
import matplotlib_venn

import matplotlib.pyplot as plt

from nltk.corpus import wordnet as wn


def main():
    wordnet = WordNetHelper()

    # Authenticate to Twitter
    with open('access_keys.json') as f_in:
        access_keys = json.load(f_in)

    auth = tweepy.OAuthHandler(access_keys["consumer_key"], access_keys["consumer_secret"])
    auth.set_access_token(access_keys["access_token"], access_keys["access_token_secret"])

    # Create API object
    api = tweepy.API(auth)

    filename = 'temp.png'

    while True:
        if os.path.exists(filename):
            os.remove(filename)

        generate_random_venn(wordnet, filename=filename)

        api.update_with_media(filename=filename)
        time.sleep(3600)


class WordNetHelper:
    """
    Retrieves information from WordNet
    """
    def __init__(self):
        self.all_synsets = list(wn.all_synsets())

    def get_random_synset(self):
        return random.choice(self.all_synsets)

    def get_subclasses(self, synset):
        return synset.hyponyms()

    def get_members(self, synset):
        return synset.hyponyms() + synset.instance_hyponyms()

    def get_name(self, synset):
        return [l.replace('_', ' ') for l in synset.lemma_names()][0]


def draw_venn3(A, B, C, set_labels=['A', 'B', 'C'], filename=None):
    """
    Draw a Venn diagram for sets A, B, and C
    """
    sets = [A, B, C]

    diagram = matplotlib_venn.venn3(sets, set_labels=set_labels)
    _ = matplotlib_venn.venn3_circles(sets, linestyle='solid', linewidth=1)

    # Abc, aBc, ABc, abC, AbC, aBC, ABC
    members = [A.difference(B.union(C)),
               B.difference(A.union(C)),
               A.intersection(B).difference(C),
               C.difference(B.union(A)),
               A.intersection(C).difference(B),
               B.intersection(C).difference(A),
               A.intersection(B).intersection(C)]

    for v, curr_members in zip(diagram.subset_labels, members):
        if v is not None:
            v.set_text(str('\n'.join(curr_members)))

    if filename is not None:
        plt.savefig(filename, format='png', bbox_inches='tight')
    else:
        plt.show()
        
        
def draw_venn2(A, B, set_labels=['A', 'B'], filename=None):
    """
    Draw a Venn diagram for sets A and B
    """
    sets = [A, B]

    diagram = matplotlib_venn.venn2(sets, set_labels=set_labels)
    _ = matplotlib_venn.venn2_circles(sets, linestyle='solid', linewidth=1)

    # A, B, AB
    members = [A.difference(B),
               B.difference(A),
               A.intersection(B)]

    for v, curr_members in zip(diagram.subset_labels, members):
        if v is not None:
            v.set_text(str('\n'.join(curr_members)))

    if filename is not None:
        plt.savefig(filename, format='png', bbox_inches='tight')
    else:
        plt.show()

        
def generate_random_venn2(intersections, sets):
    relevant_sets = [s for s, others in intersections.items() if len(others) >= 1]
        
    if len(relevant_sets) == 0:
        return None

    main_set = random.choice(relevant_sets)

    if len(intersections[main_set]) > 1:
        relevant_sets = [main_set] + random.choice(list(intersections[main_set]))
    else:
        relevant_sets = [main_set] + list(intersections[main_set])

    set_labels = relevant_sets 

    # Randomly select members 
    A, B = [set(sets[name]) for name in relevant_sets]
    all_members = [A.difference(B),
                   B.difference(A),
                   A.intersection(B)]

    all_members = [random.sample(list(members), 3) if len(members) > 3 else members for members in all_members]
    all_members = set.union(*[set(s) for s in all_members])
    sets = [set(sets[name]).intersection(all_members) for name in relevant_sets] 
    return sets, set_labels


def generate_random_venn3(intersections, sets):
    relevant_sets = [s for s, others in intersections.items() if len(others) >= 2]
        
    if len(relevant_sets) == 0:
        return None

    main_set = random.choice(relevant_sets)

    if len(intersections[main_set]) > 2:
        relevant_sets = [main_set] + random.sample(list(intersections[main_set]), 2)
    else:
        relevant_sets = [main_set] + list(intersections[main_set])

    set_labels = relevant_sets 

    # Randomly select members 
    A, B, C = [set(sets[name]) for name in relevant_sets]
    all_members = [A.difference(B.union(C)),
                   B.difference(A.union(C)),
                   A.intersection(B).difference(C),
                   C.difference(B.union(A)),
                   A.intersection(C).difference(B),
                   B.intersection(C).difference(A),
                   A.intersection(B).intersection(C)]

    all_members = [random.sample(list(members), 3) if len(members) > 3 else members for members in all_members]
    all_members = set.union(*[set(s) for s in all_members])
    sets = [set(sets[name]).intersection(all_members) for name in relevant_sets] 
    return sets, set_labels
        
    
def generate_random_venn(wordnet, filename=None):
    found = False

    while not found:
        plt.clf()
        
        # Random world to start from
        world = wordnet.get_random_synset()
        
        # All of the possible sets (dictionary of names to members) 
        subclasses = wordnet.get_subclasses(world)
        sets = {wordnet.get_name(subclass): wordnet.get_members(subclass)
                for subclass in subclasses}
        
        # Only keep sets that contain at least 3 members
        sets = {name: members for name, members in sets.items() if len(members) >= 3}

        # We need 2 or 3 sets for the Venn
        if len(sets) < 2:
            continue

        # Set name to member names
        sets = {name: [wordnet.get_name(member) for member in subclass]
                for name, subclass in sets.items()}

        # Take only sets that have intersection
        intersections = {name: {oname for oname, omems in sets.items()
                               if oname != name and len(set(mems).intersection(set(omems))) > 0} 
                         for name, mems in sets.items()}
        
        # Try 3 first
        result = generate_random_venn3(intersections, sets)
        
        if result is not None:
            sets, set_labels = result
            found = True
            draw_venn3(*sets, set_labels=set_labels, filename=filename)
        else:
            # Try 2
            result = generate_random_venn2(intersections, sets)
            if result is not None:
                sets, set_labels = result 
                found = True
                draw_venn2(*sets, set_labels=set_labels, filename=filename)


if __name__ == "__main__":
    main()