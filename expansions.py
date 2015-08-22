
import sqlite3
import random
import re
from nltk.corpus import wordnet as wn

RECORD_LIMIT = 50
MAX_ITERS = 10

categories = ["tech", "bigdata", "devops", "webscale", "language", "adj", "noun", "verb", "prefix", "suffix"]


expansions = {
    "buzzword": ["tech", "bigdata", "devops", "webscale", "language"],
    "dict": ["adj", "noun", "verb"],
    "word": ["tech", "bigdata", "devops", "webscale", "language", "adj", "noun", "verb"],
}


# TODO pull this dynamically, or at least inject it from db creation script
counts = {
    "noun": 82192,
    "suffix": 17,
    "language": 14,
    "bigdata": 49,
    "devops": 37,
    "prefix": 16,
    "verb": 13789,
    "webscale": 46,
    "tech": 33,
    "adj": 18185,
}


# TODO refactor so that module-level DB connection is not necessary
conn = sqlite3.connect("words.db")
curs = conn.cursor()

def get_words(cat):
    sql = "select word from words where %s order by random() limit %i"
    return [row[0] for row in curs.execute(sql % (categories[cat], RECORD_LIMIT))]

def words(gen, cats):
    words = gen()

    # Process category expansions, like "dict" -> "noun", "verb", "adj"
    for cat in cats:
        if cat in expansions:
            cats += expansions[cat]
            cats.remove(cat)

    for cat in cats:
        if cat[0] == "^" and cat[1:] in categories:
            cats.remove(cat[1:])

    tables = []
    for cat in cats:
        if cat in categories:
            tables.append((cat, random.randint(1, counts[cat])))

    sql = " union ".join(["select word from %s where id = %i" % t for t in tables])
    if len(tables) > 1:
        # order by random() doesn't perform so well, but good enough for this...
        # see also: http://stackoverflow.com/questions/4114940/select-random-rows-in-sqlite
        sql = "select word from (%s) order by random() limit 1" % sql

    #print sql
    curs.execute(sql)
    return str(curs.fetchone()[0])

def twice(gen):
    return gen() + gen()

def upper(gen):
    return gen().upper()

def lower(gen):
    return gen().lower()

def repeat(gen, times=2):
    times = int(times)
    return reduce((lambda l, r: l + r), [gen() for i in range(0, times)])

def repeat_decay(gen, times=2, rate=0.7):
    pass

def synonymous(gen, term):
    term = str(term)
    syns = set()
    for syn in wn.synsets(term):
        for lemma in syn.lemmas:
            syns.add(lemma.name)
    return camel_case(str(random.choice(list(syns))))

def camel_case(gen):
    if not isinstance(gen, str):
        gen = gen()
    return "".join([s[0].upper() + s[1:].lower() for s in gen.replace("_", " ").split()])

expressions = {
    ":consonant:": "[bcdfghjklmnpqrstvwxyz]+",
    ":vowel:": "[aeiou]+"
}

def ends_with(gen, expr):
    if expr in expressions:
        expr = expressions[expr]

    expr = expr + "$"

    return regex(gen, expr)

def starts_with(gen, expr):
    if expr in expressions:
        expr = expressions[expr]

    expr = "^" + expr

    return regex(gen, expr)

def regex(gen, expr):
    term = gen()
    iters = 0

    while not re.match(term, expr) and iters < MAX_ITERS:
        term = gen()
        iters += 1

    return term

filters = {
    "words": words,
    "twice": twice,
    "upper": upper,
    "lower": lower,
    "repeat": repeat,
    "synonymOf": synonymous,
    "camelCase": camel_case,
    "endsWith": ends_with,
    "startsWith": starts_with,
    "regex": regex,
}

generators = ["synonymOf", "words"]

def expand(expr):
    regex = re.compile("\{(.*?)\}")
    terms = regex.findall(expr)
    noop = lambda: []

    def mklambda(op, prev, args):
        return lambda: op(prev, *args)

    for term in terms:
        clauses = term.split("|")

        if len(clauses) is 0:
            raise Exception("No word sources specified")

        cats = clauses[0].split()
        if cats[0] not in generators:
            clauses = clauses[1:]
            ops = mklambda(words, noop, [cats])
        else:
            ops = noop

        i = 0
        for clause in clauses:
            parts = [part.strip() for part in clause.split()]
            name = parts[0]
            args = parts[1:]

            if name not in filters:
                raise Exception("Invalid filter")

            ops = mklambda(filters[name], ops, args)
            i += 1

        expr = regex.sub(ops(), expr, count=1)

    return expr


print expand("{buzzword}{suffix}")
print expand("{prefix}{buzzword|repeat 2}")
print expand("{tech|repeat 2}")
print expand("{synonymOf speedy}{suffix}")
print expand("{noun|endsWith :consonant:}ly")





