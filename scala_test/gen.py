import random
import csv

wrt = csv.writer(open("out/test.csv", "w"))

for i in range(1000):
    x1 = random.uniform(0, 100)
    x2 = random.uniform(0, 100)
    y = 5 + 20*x1 + 10*x2 + random.gauss(0, 5)
    wrt.writerow([x1, x2, y])
