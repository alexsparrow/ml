import re
import math
import pprint

import functools
import operator

def product(seq):
    """Product of a sequence."""
    return functools.reduce(operator.mul, seq, 1)

def argmax(d):
    kmax = None
    for k, v in d.items():
        if kmax is None or v > d[kmax]:
            kmax = k
    return kmax

class BayesClassify(object):
    def __init__(self, categories):
        self._categories = categories
        self._freqs = dict([(cat, {}) for cat in categories])
        self._cat_freqs = dict([(cat, 0) for cat in categories])
        self._total = 0
        self._totals = dict([(cat, 0) for cat in categories])

    def train(self, cat, words):
        self._total += 1
        self._cat_freqs[cat] += 1
        for w in words:
            self._freqs[cat][w] = self._freqs[cat].setdefault(w, 0) + 1
            self._totals[cat] += 1

    def prob(self, words, logs=False):
        probs = dict([(cat, 0) for cat in self._categories])
        for cat in self._categories:
            p = 1.0
            wprobs = [float(self._cat_freqs[cat])/self._total]
            wprobs.extend([float(self._freqs[cat].get(w, 1)) / self._totals[cat] for w in words])
            if logs: probs[cat] = math.exp(sum([math.log(p) for p in wprobs]))
            else: probs[cat] = product(wprobs)
        return probs

def load_data(fname, test=False):
    lines = open(fname).readlines()[1:]
    records = []
    for l in lines:
        f = l.split(",")
        if test:
            off = None
            ts = f[0]
            msg = f[1].strip('"').strip()
        else:
            off = [False, True][int(f[0])] 
            ts = f[1]
            msg = f[2].strip('"').strip()
        words = re.findall(r'\w+', msg)
        words = [w for w in words if len(w) > 2]
        records.append((off, ts, words, l))
    return records 

if __name__ == "__main__":
    bc = BayesClassify([True, False])
    train = load_data("data/imperium.csv")
    test = load_data("data/imperium_test.csv", test=True)
    conf = {True:{True:0, False:0},
           False:{True:0, False:0}}
    for rec in train:
        bc.train(rec[0], rec[2])
    outf = open("imperium.csv", "w")
    for rec in test:
        p = bc.prob(rec[2], logs=True)
        pnorm = p[True] + p[False]
        if pnorm == 0: pnorm = 0.000000000000001
        p = dict([(k, v/pnorm) for k, v in p.iteritems()])
        kmax = argmax(p)
        outf.write("%.3f%s" % (p[True], rec[3][rec[3].index(","):])) 
    pprint.pprint(conf)

