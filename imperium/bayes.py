# Naive Bayes classifier
import math

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

