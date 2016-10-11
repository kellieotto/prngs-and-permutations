# Mersenne Twister

from simulation_utils import *
import csv

# Boilerplate stuff

reps = int(10**3)
n = [13, 30]
k = [4, 10]
seedvalues = [100, 233424280, 429496729]


for nn in n:
    for kk in k:
        if kk >= nn:
            continue
        for ss in seedvalues:
            mt = np.random
            mt.seed(ss)

            uniqueSampleCounts = getEmpiricalDistr(mt, n=nn, k=kk, reps=reps)
            with open('../rawdata/US_MT.csv', 'at') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in uniqueSampleCounts.items():
                    writer.writerow([key, value, nn, kk, ss])
        
            itemCounts = getItemCounts(uniqueSampleCounts)    
            with open('../rawdata/FO_MT.csv', 'at') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in itemCounts.items():
                    writer.writerow([key, value, nn, kk, ss])