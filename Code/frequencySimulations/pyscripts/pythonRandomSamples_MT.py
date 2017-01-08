# Mersenne Twister

from simulation_utils import *
import csv

# Boilerplate stuff

reps = np.linspace(10**5, 10**7, num = 10**2)
reps = [int(rr) for rr in reps]
rep_diffs = [reps[i+1]-reps[i] for i in range(len(reps)-1)]
rep_diffs.insert(0, reps[0])
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
            uniqueSampleCounts = None
            
            for rr in range(len(reps)):
                uniqueSampleCounts = getEmpiricalDistr(mt, PIKK, n=nn, k=kk, reps=rep_diffs[rr], uniqueSamples=uniqueSampleCounts)
                
                chisqTestResults = conductChiSquareTest(uniqueSampleCounts)
                chisqDF_US = len(uniqueSampleCounts)-1
                chisqStatistic_US = chisqTestResults[0]
                chisqPvalue_US = chisqTestResults[1]

                rangeStat_US = np.ptp(list(uniqueSampleCounts.values()))
                rangePvalue_US = 1-distrMultinomialRange(rangeStat_US, reps[rr], comb(nn, kk))
                
                minFreq = np.min(list(uniqueSampleCounts.values()))
                maxSelectionProbRatio = (rangeStat_US + minFreq)/minFreq
            
                with open('../rawdata/US_MT_PIKK.csv', 'at') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([nn, kk, ss, reps[rr], "PIKK", "MT", 
                                    chisqStatistic_US, chisqDF_US, chisqPvalue_US, 
                                    rangeStat_US, rangePvalue_US, maxSelectionProbRatio])
