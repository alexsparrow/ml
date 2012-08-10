from bayes import BayesClassify
from utils import argmax, load_data
import pprint

if __name__ == "__main__":
    bc = BayesClassify([True, False])
    train = load_data("data/imperium.csv")
    test = load_data("data/imperium_test.csv", test=True)
    conf = {True:{True:0, False:0},
           False:{True:0, False:0}}
    for rec in train:
        bc.train(rec[0], rec[2])
    outf = open("bayes_submit.csv", "w")
    outf.write('"Insult","Date","Comment"\n')
    for rec in test:
        p = bc.prob(rec[2], logs=True)
        pnorm = p[True] + p[False]
        if pnorm == 0: pnorm = 0.000000000000001
        p = dict([(k, v/pnorm) for k, v in p.iteritems()])
        kmax = argmax(p)
        outf.write("%.3f%s" % (p[True], rec[3][rec[3].index(","):])) 
    pprint.pprint(conf)

