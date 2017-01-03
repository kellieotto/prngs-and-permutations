# Super Duper

from simulation_utils import *
import csv

# Boilerplate stuff

reps = [10**5, 5*10**5, 10**6, 5*10**6, 10**7, 5*10**7, 10**8]
rep_diffs = [reps[i+1]-reps[i] for i in range(len(reps)-1)]
rep_diffs.insert(0, reps[0])
n = [13, 30]
k = [4, 10]
seedvalues = [100, 233424280, 429496729]

# Parameters for the Super Duper LCG
A_SD = 0
B_SD = 69069
M_SD = 2**32


for nn in n:
    for kk in k:
        if kk >= nn:
            continue
        for ss in seedvalues:
            sdlcg = lcgRandom(seed=ss, A=A_SD, B=B_SD, M=M_SD)

            for rr in range(len(reps)):
                uniqueSampleCounts = getEmpiricalDistr(sdlcg, PIKK, n=nn, k=kk, reps=rep_diffs[rr], uniqueSamples=uniqueSampleCounts)
                with open('../rawdata/US_SD_PIKK.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in uniqueSampleCounts.items():
                        writer.writerow([key, value, nn, kk, ss, reps[rr], "PIKK"])
            
                itemCounts = getItemCounts(uniqueSampleCounts)    
                with open('../rawdata/FO_SD_PIKK.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in itemCounts.items():
                        writer.writerow([key, value, nn, kk, ss, reps[rr], "PIKK"])
