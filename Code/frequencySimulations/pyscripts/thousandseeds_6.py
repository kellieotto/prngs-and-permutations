# SLURM Array Job 6: Super Duper, PIKK, n=13, k=10


import numpy as np
from ipyparallel import Client
import csv


# Generate 1000 random seeds using random 32-bit integers from MT

np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 1000)
column_names = ["seed", "reps", "PopSize", "SampleSize", "chisqStat", "chisqDF",
                "chisqPvalue", "rangeStat", "rangePvalue"]
reps = np.linspace(10**5, 10**7, num = 10)
reps = [int(rr) for rr in reps]

# Parameters for the Super Duper LCG
A_SD = 0
B_SD = 69069
M_SD = 2**32

def testSeed(ss, reps):
	
	# initialize
	res_list = []
	rep_diffs = [reps[i+1]-reps[i] for i in range(len(reps)-1)]
	rep_diffs.insert(0, reps[0])
	
	# Parameters for the Super Duper LCG
	A_SD = 0
	B_SD = 69069
	M_SD = 2**32
	sdlcg = lcgRandom(seed=ss, A=A_SD, B=B_SD, M=M_SD)

	uniqueSampleCounts = None
	
	for rr in range(len(reps)):
		uniqueSampleCounts = getEmpiricalDistr(sdlcg, PIKK, n=nn, k=kk, 
		reps=rep_diffs[rr], uniqueSamples=uniqueSampleCounts)
	
		chisqTestResults = conductChiSquareTest(uniqueSampleCounts)
		chisqDF_US = len(uniqueSampleCounts)-1
		chisqStatistic_US = chisqTestResults[0]
		chisqPvalue_US = chisqTestResults[1]

		rangeStat_US = np.ptp(list(uniqueSampleCounts.values()))
		rangePvalue_US = 1-distrMultinomialRange(rangeStat_US, reps[rr], comb(nn, kk))
		
		res_list.append([ss, reps[rr], nn, kk, chisqStatistic_US, chisqDF_US, 			chisqPvalue_US, rangeStat_US, rangePvalue_US])

	return res_list

# Set up engines

c = Client()
c.ids

dview = c[:]
dview.block = True

lview = c.load_balanced_view()
lview.block = True

dview.execute('import sys')
dview.execute("sys.path.append('../../modules')")
dview.execute('from simulation_utils import *')
dview.execute('from prng import lcgRandom')
dview.execute('import numpy as np')
mydict = dict(seed_values = seed_values, testSeed = testSeed, reps = reps, nn = 13, kk = 10)
dview.push(mydict)




# need a wrapper function because map() only operates on one argument


def wrapper(i):
	return(testSeed(seed_values[i], reps = reps))



# Map it to each seed

result = lview.map(wrapper, range(len(seed_values)))
 
 

# Write results to file

with open('../rawdata/SD_1000seeds_PIKK_n13_k10.csv', 'at') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(column_names)
	for i in range(len(result)):
		for j in range(len(result[i])):
			writer.writerow(result[i][j])


# Finally we stop the worker engines:

#! ipcluster stop