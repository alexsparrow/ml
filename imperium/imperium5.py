import json
from pprint import pprint
from collections import Counter
from string import punctuation
import itertools
import csv
import datetime

punct_names = {"!":"exclamation",
               ".":"fullstop",
               ":":"colon",
               ";":"semicolon",
               "?":"question",
               ",":"comma",
               "'":"invertedcomma",
               '"':"quote",
               "#":"hash",
               "%":"percent",
               "$":"dollar",
               "&":"ampersand",
               "@":"at-sign",
               "~":"tilde",
               "(":"paren",
               ")":"paren"
               }


class Counts:
    def __init__(self, categories):
        self._categories = categories
        self._word_count = dict([(cat, Counter()) for cat in self._categories])
        self._tag_count = dict([(cat, Counter()) for cat in self._categories])
        self._ne_count = dict([(cat, Counter()) for cat in self._categories])
        self._punct_count = dict([(cat, Counter()) for cat in self._categories])

    def word(self, cat, word):
        self._word_count[cat][word] += 1
    def tag(self, cat, tag):
        self._tag_count[cat][tag] += 1
    def ne(self, cat, ne):
        self._ne_count[cat][ne] += 1

    def prune(self):
        for cat in self._categories:
            remove = []
            for word, freq in self._word_count[cat].iteritems():
                if len(word) == 1 and word in punct_names: 
                    self._punct_count[cat][punct_names[word]] = freq
                    remove.append(word)
                elif len(word) <= 2: remove.append(word)
                elif "\\" in word: remove.append(word)
            for r in remove: del self._word_count[cat][r]

    def distinctive(self, coll):
        diffs = {}
        totals = dict([(cat, sum(coll[cat].values())) for cat in self._categories])
        sds = []
        all_things = set(itertools.chain(*[coll[cat].keys() for cat in self._categories]))
        for thing in all_things: 
            props = [float(coll[cat][thing])/totals[cat] for cat in self._categories]
            mean = sum(props)/len(props)
            sd = sum([(prop - mean)**2 for prop in props])/len(props)
            sds.append((thing, sd))
        return sorted(sds, key=lambda x:x[1], reverse=True)

    def most_common(self, coll):
        all_things = set(itertools.chain(*[coll[cat].keys() for cat in self._categories]))
        all_count = Counter()
        for cat, count in coll.iteritems():
            all_count += count 
        return all_count.most_common()
    
    def get_all(self, coll):
        p = set()
        for counts in coll.values():
            for key in counts.keys():
                p.add(key)
        return p 

def make_bag(vals):
    return dict([(val, idx) for idx, val in enumerate(vals)])

def make_vector(bag, vals):
    v = [0]*len(bag)
    for val in vals:
        if val in bag: v[bag[val]] += 1
    return v

def run(fname, word_bag, tag_bag, punct_bag, ne_bag):
    for rec in json.load(open(fname)):
        vals = []
        if "Insult" in rec: vals.append(rec["Insult"])
        else: vals.append(0)
        if len(rec["Date"].strip()):
            y = int(rec["Date"][:4])
            m = int(rec["Date"][4:6])
            d = int(rec["Date"][6:8])
            h = int(rec["Date"][8:10])
            dt = datetime.date(y, m,d)
            vals.append(int(rec["Date"][8:10]))
            vals.append(dt.weekday())
        else:
            vals.extend(["NA", "NA"])
        vals.append(len(rec["words_nltk"]))
        vals.append(sum([len(word) for word in rec["words_nltk"]])/float(len(rec["words_nltk"])))
        vals.extend(make_vector(word_bag, rec["words_nltk"]))
        vals.extend(make_vector(tag_bag, rec["pos_tag"]))
        punct = [punct_names[wd] for wd in rec["words_nltk"] if wd in punct_names]
        vals.extend(make_vector(punct_bag, punct))
        vals.extend(make_vector(ne_bag, rec["ne_tags"]))

        
        yield vals

if __name__ == "__main__":
    n_words_top_by_sd = 200 # was 100
    n_words_total = 300 # was 200 

    n_tags_top_by_sd = 30
    n_tags_total = 50

    c = Counts([0,1])
    for rec in json.load(open("process/train.json")):
        insult = int(rec["Insult"])
        for word in rec["words_nltk"]: c.word(insult, word.lower())
        for tag in rec["pos_tag"]: c.tag(insult, tag)
        for ne in rec["ne_tags"]: c.ne(insult, ne)
    c.prune()
    words = set([wd for wd, sd in c.distinctive(c._word_count)[:n_words_top_by_sd]])
    for word, freq in c.most_common(c._word_count):
        if len(words) == n_words_total:
            break
        words.add(word)
   
    tags = set([tag for tag, sd in c.distinctive(c._tag_count)[:n_tags_top_by_sd]])
    for tag, freq in c.most_common(c._tag_count):
        if len(tags) == n_tags_total: break
        else: tags.add(tag)

    word_bag = make_bag(words)
    tag_bag = make_bag(tags)
   
    punct_bag = make_bag(c.get_all(c._punct_count))
    print punct_bag
    ne_bag = make_bag(c.get_all(c._ne_count))
   
    csv_header = ["Response", "Hour", "Weekday", "NWords", "AvgWordLength"]
    def bag_names(bag, prefix):
        items = sorted(bag.items(), key = lambda x : x[1])
        return ["%s_%s" % (prefix, name) for name, _ in items] 

    csv_header += bag_names(word_bag, "Word")
    csv_header += bag_names(tag_bag, "Tag")
    csv_header += bag_names(punct_bag, "Punct")
    csv_header += bag_names(ne_bag, "NE")

    writer = csv.writer(open("process/wordbag2_train.csv", "w"))
    writer.writerow(csv_header)
    for obj in run("process/train.json", word_bag, tag_bag, punct_bag, ne_bag):
        writer.writerow(obj)
    writer = csv.writer(open("process/wordbag2_test.csv", "w"))
    writer.writerow(csv_header)
    for obj in run("process/test.json", word_bag, tag_bag, punct_bag, ne_bag):
        writer.writerow(obj)
