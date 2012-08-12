import csv
import re
import json
from pprint import pprint

import nltk.tag
from nltk.chunk import ne_chunk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag.brill import *
tagger = None

from collections import Counter
word_counter = Counter({})

def train_tagger():
    from nltk.corpus import brown
    brown_train = brown.tagged_sents(categories='news')[:1000]
    regexp_tagger = nltk.RegexpTagger(
              [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
                      (r'(The|the|A|a|An|an)$', 'AT'),   # articles
                      (r'.*able$', 'JJ'),                # adjectives
                      (r'.*ness$', 'NN'),                # nouns formed from adjectives
                      (r'.*ly$', 'RB'),                  # adverbs
                      (r'.*s$', 'NNS'),                  # plural nouns
                      (r'.*ing$', 'VBG'),                # gerunds
                      (r'.*ed$', 'VBD'),                 # past tense verbs
                      (r'.*', 'NN')                      # nouns (default)
                 ])
    unigram_tagger = nltk.UnigramTagger(brown_train, backoff=regexp_tagger)
    templates = [
        SymmetricProximateTokensTemplate(ProximateTagsRule, (1,1)),
        SymmetricProximateTokensTemplate(ProximateTagsRule, (2,2)),
        SymmetricProximateTokensTemplate(ProximateTagsRule, (1,2)),
        SymmetricProximateTokensTemplate(ProximateTagsRule, (1,3)),
        SymmetricProximateTokensTemplate(ProximateWordsRule, (1,1)),
        SymmetricProximateTokensTemplate(ProximateWordsRule, (2,2)),
        SymmetricProximateTokensTemplate(ProximateWordsRule, (1,2)),
        SymmetricProximateTokensTemplate(ProximateWordsRule, (1,3)),
        ProximateTokensTemplate(ProximateTagsRule, (-1, -1), (1,1)),
        ProximateTokensTemplate(ProximateWordsRule, (-1, -1), (1,1)),
    ]
    trainer = FastBrillTaggerTrainer(initial_tagger=unigram_tagger,
                                   templates=templates, trace=3,
                                   deterministic=True)
    brill_tagger = trainer.train(brown_train, max_rules=10)
    return brill_tagger

def data(fname):
    reader = csv.DictReader(open(fname))
    idx = 0
    for row in reader:
        if idx % 100 == 0: print "Row %d" % idx
        row["words_basic"] = re.findall(r'\w+', row["Comment"])
        row["words_nltk"] = word_tokenize(row["Comment"])
        row["pos_tag"] = []
        row["ne_tags"] = []
        for sent in sent_tokenize(row["Comment"]):
            words = tagger.tag(word_tokenize(sent))
            row["pos_tag"].extend([wd[1] for wd in words])
            for x in ne_chunk(words):
                if x.__class__.__name__ == "Tree":
                    row["ne_tags"].append(x.node)
        yield row
        idx += 1

if __name__ == "__main__":
    tagger = train_tagger() 
    d = data("data/imperium.csv")
    json.dump(list(d), open("process/train.json", "w"), indent=1) 
    d = data("data/imperium_test.csv")
    json.dump(list(d), open("process/test.json", "w"), indent=1)
