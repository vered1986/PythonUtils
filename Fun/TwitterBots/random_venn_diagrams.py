import time
import json
import tweepy
import random
import matplotlib_venn

import matplotlib.pyplot as plt

from collections import defaultdict
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
        try:
            generate_random_venn(wordnet, filename=filename)
            api.update_with_media(filename=filename)
            time.sleep(3600)
        except:
            pass


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


def draw_venn(A, B, C, set_labels=['A', 'B', 'C'], filename=None):
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


def generate_random_venn(wordnet, filename=None):
    found = False

    while not found:
        set_by_member = defaultdict(set)
        world = wordnet.get_random_synset()
        subclasses = wordnet.get_subclasses(world)
        sets = {wordnet.get_name(subclass): wordnet.get_members(subclass)
                for subclass in subclasses}
        sets = {name: members for name, members in sets.items()
                if len(members) >= 3}

        if len(sets) < 3:
            continue

        sets = {name: [wordnet.get_name(member) for member in subclass]
                for name, subclass in sets.items()}

        # Make sure there is some intersection
        [set_by_member[member].add(name)
         for name, members in sets.items() for member in members]
        members_in_intersection = {member
                                   for member, curr_sets in set_by_member.items()
                                   if len(curr_sets) > 1}

        relevant_sets = set([s
                             for member, curr_sets in set_by_member.items()
                             for s in curr_sets
                             if member in members_in_intersection])

        sets = {name: members for name, members in sets.items()
                if name in relevant_sets}

        if len(sets) < 3:
            continue

        sets = list(sets.items())
        sets = random.sample(sets, 3) if len(sets) > 3 else sets
        set_labels, sets = zip(*sets)

        new_sets = []
        for s in sets:
            if len(s) > 5:
                members_int = list(set(s).intersection(members_in_intersection))
                if len(members_int) > 3:
                    members_int = random.sample(members_int, 3)
                s = random.sample(s, 5 - len(members_int)) + members_int
            new_sets.append(set(s))

        found = True

    draw_venn(*new_sets, set_labels=set_labels, filename=filename)


if __name__ == "__main__":
    main()