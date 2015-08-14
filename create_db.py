#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Jeremy <Jeremy@Jeremys-MBP>
#
# Distributed under terms of the MIT license.

"""

"""

import argparse
import csv
import os
import sqlite3
import sys
import re


# Parse CLI arguments
parser = argparse.ArgumentParser(description="Word database generation script")
parser.add_argument("--wordnet", action="store", dest="wordnet_path", default="dict", help="Location of WordNet database files")
parser.add_argument("--db", action="store", dest="db_path", default="words.db", help="Path to destination database")
args = parser.parse_args()

wordnet_path = args.wordnet_path
db_path = args.db_path


conn = sqlite3.connect(db_path)
curs = conn.cursor()


sql = "create table %s (id integer primary key, word text)"
tables = ["suffix", "prefix", "webscale", "noun", "verb", "adj", "language", "bigdata", "tech", "devops"]
for table in tables:
    try:
        curs.execute("drop table %s" % table)
    except OperationalError:
        pass
    curs.execute(sql % table)

conn.commit()

with open("buzzwords.csv", "r") as f:

    reader = csv.DictReader(f)

    def insert(cat, word):
        sql = "insert into %s (word) values (?)" % cat
        curs.execute(sql, (word, ))

    for row in reader:
        for key in row:
            if key[0:3] == "is_" and row[key]:
                insert(key[3:], row["word"])


def read_wordnet(curs, pos, path=wordnet_path):
    sql = "insert into %s (word) values (?)" % pos
    regex = re.compile("^[0-9].*")

    with open(os.path.join(path, "data." + pos), "r") as f:
        for line in f:
            if regex.match(line):
                terms = []
                for term in line.split()[4].replace("-", "_").split("_"):
                    terms.append(term.strip().capitalize())

                word = "".join(terms)
                curs.execute(sql, (word, ))

read_wordnet(curs, "adj")
read_wordnet(curs, "noun")
read_wordnet(curs, "verb")

conn.commit()


counts = {}
for table in tables + ["adj", "noun", "verb"]:
    curs.execute("select count(*) from %s" % table)
    counts[table] = curs.fetchone()[0]

print "Record counts:"
print counts

conn.close()

