
import sqlite3
import random
import re
from nltk.corpus import wordnet as wn

RECORD_LIMIT = 50

categories = {
    "tech": "is_tech=1",
    "bigdata": "is_bigdata=1",
    "datascience": "is_bigdata=1",
    "devops": "is_devops=1",
    "suffix": "is_suffix=1",
    "prefix": "is_prefix=1",
    "language": "is_language=1",
    "webscale": "is_webscale=1",
    "word": "is_word=1",
    "buzzword": "is_buzzword=1",
    "dict": "is_dict=1",
    "adj": "is_adj=1",
    "noun": "is_noun=1",
    "verb": "is_verb=1",
}

conn = sqlite3.connect("words.db")
curs = conn.cursor()

def get_words(cat):
    # order by random() doesn't perform so well, but good enough for this...
    # see also: http://stackoverflow.com/questions/4114940/select-random-rows-in-sqlite
    sql = "select word from words where %s order by random() limit %i"
    return [row[0] for row in curs.execute(sql % (categories[cat], RECORD_LIMIT))]

def words(gen, cats):
    words = gen()
    for cat in cats:
        if cat in categories:
            words += get_words(cat)
    return random.choice(words)

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
        for lemma in syn.lemmas():
            syns.add(lemma.name())
    return camel_case(str(random.choice(list(syns))))

def camel_case(gen):
    if not isinstance(gen, str):
        gen = gen()
    return "".join([s[0].upper() + s[1:].lower() for s in gen.replace("_", " ").split()])

filters = {
    "words": words,
    "twice": twice,
    "upper": upper,
    "lower": lower,
    "repeat": repeat,
    "synonymOf": synonymous,
    "camelCase": camel_case,
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








