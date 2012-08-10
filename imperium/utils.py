import re
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


