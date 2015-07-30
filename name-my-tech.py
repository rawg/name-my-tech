#!/usr/env/bin/python

import random
import sys
import os
import argparse


# Parse CLI arguments
parser = argparse.ArgumentParser(description="Name my technology!")
parser.add_argument("--wordnet", action="store", dest="wordnet_path", help="Location of WordNet database files")
parser.add_argument("amount", action="store", type=int, default=10, metavar="N", help="Number of names to generate")
args = parser.parse_args()

amount = args.amount
wordnet_path = args.wordnet_path


# Read words from WordNet by part of speech
def wordnet_dict(pos, path):
    words = []
    with open(os.path.join(path, "data." + pos), 'r') as f:
        for line in f:
            words.append("".join([term.capitalize() for term in line.split(" ")[4].split("_")]))

    return words

nouns = wordnet_dict("noun", wordnet_path)
verbs = wordnet_dict("verb", wordnet_path)
adjectives = wordnet_dict("adj", wordnet_path)

# A list of Big Data buzz words
buzzy = [
    "Algorithm",
    "Auth",
    "Base",
    "Bit",
    "Byte",
    "Cask",
    "Cell",
    "Cloud",
    "Coast",
    "Column",
    "Connect",
    "DB",
    "Data",
    "Dev",
    "Dist",
    "Duty",
    "Force",
    "Forge",
    "Grid",
    "Hub",
    "Learning",
    "Log",
    "MQ",
    "Machine",
    "Mem",
    "Memory",
    "Mod",
    "Ops",
    "Parse",
    "Persist",
    "Pub",
    "Row",
    "Scale",
    "Science",
    "Script",
    "Send",
    "Socket",
    "Space",
    "Speed",
    "Stash",
    "Store",
    "Sub",
    "Team",
    "Tech",
    "Titan",
    "Web",
    "Word",
    "Work",
]


# A list of hip technology names
tech = [
    "Akka",
    "Cassandra",
    "Chef",
    "Docker",
    "Drill",
    "Erlang",
    "Giraph",
    "HBase",
    "Hadoop",
    "Haskell",
    "Hive",
    "Java",
    "Mongo",
    "PHP",
    "Puppet",
    "Python",
    "Rabbit",
    "Riak",
    "Ruby",
    "Scala",
    "Spark",
    "Vagrant",
]

# Terms that can only exist at the beginning of a name
head = [
    "Ad",
    "Big",
    "Broad",
    "Elastic",
    "Fluid",
    "Inno",
    "J",
    "ML",
    "Navi",
    "Open",
    "Py",
    "Wi",
]

# Terms that can only exist at the end of a name
tail = [
    "Buster",
    "Cast",
    "Caster",
    "FS",
    "IO",
    "MQ",
    "One",
    "QL",
    "R",
    "X",
    "lang",
    "ly",
]


# Name a technology
def tech_name():
    length = random.randint(2, 3)
    parts = []
    has_tech = False
    has_dict = False

    while len(parts) < length:
        choice = random.randint(1, 10)
        is_head = len(parts) == 0
        is_tail = len(parts) == length - 1

        if choice < 1 and (is_head or is_tail) and not has_dict:
            has_dict = True
            if is_head:
                term = random.choice(adjectives)
            elif is_tail:
                term = random.choice(verbs)

        elif choice < 2 and not has_dict:
            has_dict = True
            term = random.choice(nouns)

        elif choice < 4 and not has_tech:
            has_tech = True
            term = random.choice(tech)

        else:
            if is_tail:
                term = random.choice(buzzy + tail)
            elif is_head:
                term = random.choice(buzzy + head)
            else:
                term = random.choice(buzzy)

        if term not in parts:
            parts.append(term)

    return "".join(parts)



for i in range(1, amount):
    print(tech_name())
