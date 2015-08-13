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

try:
    curs.execute("drop table words")
except OperationalError:
    pass

ddl = """
create table words (
  id integer primary key,
  word text,

  is_suffix integer default 0,
  is_prefix integer default 0,
  is_webscale integer default 0,
  is_noun integer default 0,
  is_verb integer default 0,
  is_adj integer default 0,
  is_dict integer default 0,
  is_bigdata integer default 0,
  is_language integer default 0,
  is_tech integer default 0,
  is_buzzword integer default 0,
  is_word integer default 0,
  is_devops integer default 0

)
"""

curs.execute(ddl)


def read_wordnet(curs, pos, path=wordnet_path):
    sql = "insert into words (word, is_%s, is_word, is_dict) values (?, 1, 1, 1)" % pos
    regex = re.compile("^[0-9].*")

    with open(os.path.join(path, "data." + pos), "r") as f:
        for line in f:
            if regex.match(line):
                terms = []
                for term in line.split()[4].split("_"):
                    terms.append(term.strip().capitalize())

                word = "".join(terms)
                curs.execute(sql, (word, ))

read_wordnet(curs, "adj")
read_wordnet(curs, "noun")
read_wordnet(curs, "verb")

conn.commit()

with open("buzzwords.csv", "r") as f:
    sql = "insert into words (word, is_suffix, is_prefix, is_webscale, is_bigdata, is_language, is_tech, is_devops, is_buzzword, is_word) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    reader = csv.reader(f)
    reader.next()

    for row in reader:
        curs.execute(sql, row)

conn.commit()
conn.close()

