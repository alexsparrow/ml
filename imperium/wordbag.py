
class WordBag(object):
    def __init__(self):
        self._bag = {}

    def process(self, words):
        for w in words:
            w = w.lower()
            self._bag[w] = self._bag.setdefault(w, 0) + 1

    def bag(self, n = None, f = None):
        wbag = sorted(self._bag.iteritems(), key = lambda x : x[1], reverse=True)
        if n is not None and n < len(wbag): 
            wbag = wbag[:n] 
        if f is not None:
            wbag = [x for x in wbag if f(x)]
        return dict([(x[0], idx) for idx, x in enumerate(wbag)])
    
    @staticmethod
    def vector(words, wbag):
        v = [0]*len(wbag)
        for w in words:
            w = w.lower()
            if w in wbag: v[wbag[w]] += 1
        return v

if __name__ == "__main__":
    w = WordBag()
    print w.process("Hello there you weird hello".split())
    bag = w.bag(10) 
    print w.vector("You smell weird".split(), bag)

  
