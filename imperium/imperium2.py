from utils import load_data
from wordbag import WordBag

def run(fname, recs, bag, test=False):
    out = open(fname, "w")
    if not test: out.write("Response,")
    out.write(",".join(["WB%d" % x for x in range(len(bag))]))
    out.write("\n")
    for rec in recs:
        if not test: out.write({True:"1", False:"0"}[rec[0]] + ",") 
        out.write(",".join(["%d" % s for s in WordBag.vector(rec[2], bag)]))
        out.write("\n")

def cmp(fname1, fname2):
    in1 = open(fname1)
    in2 = open(fname2)
    vals = [(x.split(",")[0], y.split(",")[0]) for x, y in zip(in1.readlines(), in2.readlines())]
    del vals[0]
    vals = [(float(x), float(y)) for x, y in vals]
    agree = 0
    disagree = 0
    for v1, v2 in vals:
        print v1, v2
        if (v1 > 0.5) == (v2 > 0.5): agree += 1
        else: disagree +=1
    print "Agree=%d, Disagree=%d" % (agree, disagree)

if __name__ == "__main__":
    wbag = WordBag()
    train = load_data("data/imperium.csv")
    good = {}
    good_tot = 0
    bad = {}
    bad_tot = 0

    # Bag the words and also tally the number of insults non-insults in training sets
    for rec in train:
        wbag.process(rec[2])
        for w in rec[2]:
            if rec[0]: 
                bad[w] = bad.setdefault(w, 0) + 1
                bad_tot += 1
            else: 
                good[w] = good.setdefault(w, 0) + 1
                good_tot += 1
    
    # Top 300 words by frequency
    bag = wbag.bag(300)

    # For each word calculate the difference in proportions of between the good/bad set
    diffs = []
    for word, idx in bag.iteritems():
        diff = abs(float(good.get(word, 0))/good_tot - float(bad.get(word, 0))/bad_tot)
        diffs.append((word, idx, diff))

    # Take the 100 most distinguishing words as a feature vector
    diffs.sort(key = lambda x: x[2], reverse=True)
    bag_filtered = {}
    for new_idx, x in enumerate(diffs[:100]):
        bag_filtered[x[0]] = new_idx
    
    # Output training file
    run("wordbag_train.csv", train, bag_filtered) 

    # Output test file
    recs_test = load_data("data/imperium_test.csv", test=True)
    run("wordbag_test.csv", recs_test, bag_filtered, test=True)
