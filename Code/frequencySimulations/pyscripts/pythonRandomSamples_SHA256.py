# SHA-256 PRNG

import csv
from simulation_utils import *
from sha256prng import SHA256
# Boilerplate stuff

reps = [10**5, 5*10**5, 10**6, 5*10**6, 10**7, 5*10**7, 10**8]
rep_diffs = [reps[i+1]-reps[i] for i in range(len(reps)-1)]
rep_diffs.insert(0, reps[0])
n = [13, 30]
k = [4, 10]
seedvalues = [100, 233424280, 429496729]


for nn in n:
    for kk in k:
        if kk >= nn or (n == 30 and k == 10):
            continue
        for ss in seedvalues:
            prng = SHA256(ss)
            uniqueSampleCounts = None

            for rr in range(len(reps)):
                uniqueSampleCounts = getEmpiricalDistr(prng, PIKK, n=nn, k=kk, reps=rep_diffs[rr], uniqueSamples=uniqueSampleCounts)
                with open('../rawdata/US_SHA256_PIKK.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in uniqueSampleCounts.items():
                        writer.writerow([key, value, nn, kk, ss, reps[rr], "PIKK"])
            
                itemCounts = getItemCounts(uniqueSampleCounts)    
                with open('../rawdata/FO_SHA256_PIKK.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in itemCounts.items():
                        writer.writerow([key, value, nn, kk, ss, reps[rr], "PIKK"])
