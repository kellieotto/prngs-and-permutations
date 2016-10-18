# Super Duper

from simulation_utils import *
import csv

# Boilerplate stuff

reps = int(10**9)
n = [13, 30]
k = [4, 10]
seedvalues = [100, 233424280]

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

            uniqueSampleCounts = getEmpiricalDistr(sdlcg, n=nn, k=kk, reps=reps)
            with open('../rawdata/US_SD.csv', 'at') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in uniqueSampleCounts.items():
                    writer.writerow([key, value, nn, kk, ss])
            
            itemCounts = getItemCounts(uniqueSampleCounts)    
            with open('../rawdata/FO_SD.csv', 'at') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in itemCounts.items():
                    writer.writerow([key, value, nn, kk, ss])
