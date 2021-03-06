# Mersenne Twister

from simulation_utils import *
import csv
sys.path.append('../../modules')
from sample import PIKK, fykd, fykd_sample, Random_Sample, Algorithm_R

# Boilerplate stuff

reps = [10**5, 5*10**5, 10**6, 5*10**6, 10**7]
rep_diffs = [reps[i+1]-reps[i] for i in range(len(reps)-1)]
rep_diffs.insert(0, reps[0])
n = [13, 30]
k = [4, 10]
seedvalues = [100, 233424280, 429496729]


for nn in n:
    for kk in k:
        if kk >= nn or (kk == 10 and nn == 30):
            continue
        for ss in seedvalues:

            # FYKD Shuffle
            mt = np.random
            mt.seed(ss)
            uniqueSampleCounts = None
            
            for rr in range(len(reps)):
                uniqueSampleCounts = getEmpiricalDistr(mt, fykd_sample, n=nn, k=kk, reps=rep_diffs[rr], uniqueSamples=uniqueSampleCounts)
                with open('../rawdata/US_MT_sampling.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in uniqueSampleCounts.items():
                        writer.writerow([key, value, nn, kk, ss, reps[rr], "FYKD"])
        
                itemCounts = getItemCounts(uniqueSampleCounts)    
                with open('../rawdata/FO_MT_sampling.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    for key, value in itemCounts.items():
                        writer.writerow([key, value, nn, kk, ss, reps[rr], "FYKD"])