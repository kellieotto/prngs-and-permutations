# SHA-256 PRNG

import csv
from simulation_utils import *
from sha256prng import SHA256
# Boilerplate stuff

reps = int(10**9)
n = [13, 30]
k = [4, 10]
seedvalues = [100, 233424280, 429496729]


for nn in n:
    for kk in k:
        if kk >= nn:
            continue
        for ss in seedvalues:
            prng = SHA256(ss)

            uniqueSampleCounts = getEmpiricalDistr(prng, n=nn, k=kk, reps=reps)
            with open('../rawdata/US_SHA256.csv', 'at') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in uniqueSampleCounts.items():
                    writer.writerow([key, value, nn, kk, ss])
        
            itemCounts = getItemCounts(uniqueSampleCounts)    
            with open('../rawdata/FO_SHA256.csv', 'at') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in itemCounts.items():
                    writer.writerow([key, value, nn, kk, ss])
