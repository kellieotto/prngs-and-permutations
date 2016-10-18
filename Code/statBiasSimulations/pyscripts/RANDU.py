# RANDU

from simulation_utils import *
import csv

# Boilerplate stuff

reps = int(10**3)
n = [13, 30]
k = [4, 10]
ss = 100

for nn in n:
    for kk in k:
        if kk >= nn:
            continue
        
        lcg = lcgRandom(seed=ss) # set seed of RANDU to 100

        uniqueSampleCounts = getEmpiricalDistr(lcg, n=nn, k=kk, reps=reps)
        with open('../rawdata/US_RANDU.csv', 'at') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in uniqueSampleCounts.items():
                writer.writerow([key, value, nn, kk, ss])
        
        itemCounts = getItemCounts(uniqueSampleCounts)    
        with open('../rawdata/FO_RANDU.csv', 'at') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in itemCounts.items():
                writer.writerow([key, value, nn, kk, ss])
