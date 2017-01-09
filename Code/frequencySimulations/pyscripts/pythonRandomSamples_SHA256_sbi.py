# SHA-256 PRNG

import csv
from simulation_utils import *
from sha256prng import SHA256
sys.path.append('../../modules')
from sample import sample_by_index


# Boilerplate stuff

reps = np.linspace(10**5, 10**7, num = 10**2)
reps = [int(rr) for rr in reps]
rep_diffs = [reps[i+1]-reps[i] for i in range(len(reps)-1)]
rep_diffs.insert(0, reps[0])
n = [13, 30]
k = [3, 4, 10]
seedvalues = [100, 233424280, 429496729]


for nn in n:
    for kk in k:
        if kk >= nn or (nn == 30 and kk != 4):
            continue
        for ss in seedvalues:
            prng = SHA256(ss)
            uniqueSampleCounts = None

            for rr in range(len(reps)):
                uniqueSampleCounts = getEmpiricalDistr(prng, sample_by_index, n=nn, k=kk, reps=rep_diffs[rr], uniqueSamples=uniqueSampleCounts)

                chisqTestResults = conductChiSquareTest(uniqueSampleCounts)
                chisqDF_US = len(uniqueSampleCounts)-1
                chisqStatistic_US = chisqTestResults[0]
                chisqPvalue_US = chisqTestResults[1]

                rangeStat_US = np.ptp(list(uniqueSampleCounts.values()))
                rangePvalue_US = 1-distrMultinomialRange(rangeStat_US, reps[rr], comb(nn, kk))
            
                minFreq = np.min(list(uniqueSampleCounts.values()))
                maxSelectionProbRatio = (rangeStat_US + minFreq)/minFreq
            
                with open('../rawdata/US_SHA256_sbi.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([nn, kk, ss, reps[rr], "sample_by_index", "SHA256", 
                                    chisqStatistic_US, chisqDF_US, chisqPvalue_US, 
                                    rangeStat_US, rangePvalue_US, maxSelectionProbRatio])