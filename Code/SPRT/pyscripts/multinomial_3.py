################################################################################
# SLURM Array Job 3
# SPRT of sample probabilities (multinomial equal p), SD, n=13, k=3,s = (5,10,15,20), PIKK
################################################################################

import numpy as np
import csv
from scipy.misc import comb
from ipyparallel import Client
import os

import sys
sys.path.append('../../modules')
from sample import PIKK, sample_by_index
from prng import lcgRandom

np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 1000)
s = [5, 10, 15, 20]
column_names = ["prng", "algorithm", "seed", "n", "k"]
for ss in s:
    for alt in ["_upper", "_lower"]:
        column_names.append("decision_s" + str(ss) + alt)
        column_names.append("LR_s" + str(ss) + alt)
        column_names.append("steps_s" + str(ss) + alt)
        
################################################################################
# SPRT functions
################################################################################


def sequential_multinomial_test(sampling_function, num_categories, alpha, beta, multiplier, \
                                s = None, maxsteps=10**7):
    '''
    Conduct Wald's SPRT for multinomial distribution with num_categories categories
    Let p = sum_{s most frequent categories} p_category
    H_0: selection probabilities are all 1/num_categories so p=s/num_categories
    H_1: p = p1 = multiplier * s/num_categories
    
    sampling_function: a function which generates a random number or random sample.
    num_categories: number of categories
    alpha: desired type 1 error rate
    beta: desired power
    multiplier: value larger than 1. Determines alternative: p1 = multiplier * s/num_categories
    s: tuning parameter, integer between 1 and k. Default is 1% of num_categories.
    '''

    assert multiplier > 1
    assert maxsteps > 0
    
    if s is None:
        s = [math.ceil(0.01*num_categories)]
    if isinstance(s, int):
        s = [s]

    k = num_categories # Rename for ease of use!
    lessthan_multiplier = 2 - multiplier
    
    # Set parameters
    lower = beta/(1-alpha)
    upper = (1-beta)/alpha

    # Initialize counter
    sampleCounts = dict()
    while len(sampleCounts.keys()) < max(s):
        Xn = str(sorted(sampling_function()))
        if Xn not in sampleCounts.keys():
            sampleCounts[Xn] = 0
    steps = 0
    LR_upper = {ss: [1] for ss in s}
    decision_upper = {ss: "None" for ss in s}
    num_steps_upper = {ss: maxsteps for ss in s}
    LR_lower = {ss: [1] for ss in s}
    decision_lower = {ss: "None" for ss in s}
    num_steps_lower = {ss: maxsteps for ss in s}    
    tests_running = len(s)*2
    
    # Draw samples
    while tests_running and steps < maxsteps:
        Xn = str(sorted(sampling_function()))
        top_categories = sorted(sampleCounts, key = sampleCounts.get, reverse = True)
        
        steps += 1
        for ss in s:
            # Run test for greater than alternative
            # Event occurs if Xn is among the s most frequent values of X1,...,X_n-1
            if Xn in top_categories[:ss]:
                LR_upper[ss].append(LR_upper[ss][-1] * multiplier) # p1/p0 = multiplier
            else:
                LR_upper[ss].append(LR_upper[ss][-1] * (1 - multiplier*ss/k)/(1-ss/k)) # (1-p1)/(1-p0)

            # Run test at step n
            if LR_upper[ss][-1] <= lower:
                # accept the null and stop
                decision_upper[ss] = 0
                num_steps_upper[ss] = steps
                tests_running -= 1
                if decision_lower[ss] != "None":
                    s.remove(ss)
                
            if LR_upper[ss][-1] >= upper:
                # reject the null and stop
                decision_upper[ss] = 1
                num_steps_upper[ss] = steps
                tests_running -= 1
                if decision_lower[ss] != "None":
                    s.remove(ss)
            
            # Run test for less than alternative
            # Event occurs if Xn is among the s least frequent values of X1,...,X_n-1
            if Xn in top_categories[-ss:]:
                LR_lower[ss].append(LR_lower[ss][-1] * lessthan_multiplier) # p1/p0 = lessthan_multiplier
            else:
                LR_lower[ss].append(LR_lower[ss][-1] * (1 - lessthan_multiplier*ss/k)/(1-ss/k)) # (1-p1)/(1-p0)

            # Run test at step n
            if LR_lower[ss][-1] <= lower:
                # accept the null and stop
                decision_lower[ss] = 0
                num_steps_lower[ss] = steps
                tests_running -= 1
                if decision_upper[ss] != "None":
                    s.remove(ss)
                
            if LR_lower[ss][-1] >= upper:
                # reject the null and stop
                decision_lower[ss] = 1
                num_steps_lower[ss] = steps
                tests_running -= 1
                if decision_upper[ss] != "None":
                    s.remove(ss)

        # add Xn to sampleCounts and repeat
        if Xn in sampleCounts.keys():
            sampleCounts[Xn] += 1
        else:
            sampleCounts[Xn] = 1
    return {'decision_upper' : decision_upper,
            'decision_lower' : decision_lower,
            'lower_threshold' : lower,
            'LR_upper' : LR_upper,
            'LR_lower' : LR_lower,
            'upper_threshold' : upper,
            'steps_upper' : num_steps_upper,
            'steps_lower' : num_steps_lower
            }
            
################################################################################
# Wrapper functions
################################################################################

def testSeed(ss, n, k, s):

    prng = lcgRandom(seed=ss, A=0, B=69069, M=2**32)
    
    sampling_func = lambda: PIKK(n, k, prng)
    res = sequential_multinomial_test(sampling_func, num_categories=comb(n, k), alpha=0.05/2, beta=0, multiplier=1.01, s=s)

    unpack = ["SD", "PIKK", ss, n, k]
    for svalue in s:
        unpack.append(res['decision_upper'][svalue])
        unpack.append(res['LR_upper'][svalue][-1])
        unpack.append(res['steps_upper'][svalue])
        unpack.append(res['decision_lower'][svalue])
        unpack.append(res['LR_lower'][svalue][-1])
        unpack.append(res['steps_lower'][svalue])
    return unpack
    

def wrapper(i):
    return(testSeed(seed_values[i]))
    
################################################################################
# Set up engines
################################################################################
arrayid = int(os.environ['SLURM_ARRAY_TASK_ID'])
mycluster = "cluster-" + str(arrayid)

c = Client(profile=mycluster)
c.ids

dview = c[:]
dview.block = True

lview = c.load_balanced_view()
lview.block = True

dview.execute('import sys')
dview.execute("sys.path.append('../../modules')")
dview.execute('from sample import PIKK, sample_by_index')
dview.execute('from prng import lcgRandom')
dview.execute('from scipy.misc import comb')
dview.execute('import numpy as np')
mydict = dict(seed_values = seed_values, 
              testSeed = testSeed,
              sequential_multinomial_test = sequential_multinomial_test,
              s = s)
dview.push(mydict)
    

################################################################################
# Execute
################################################################################

# Map it to each seed

#result = list(map(wrapper, range(len(seed_values))))
result = lview.map(lambda ss: testSeed(ss, n=13, k=3, s=10), seed_values)


# Write results to file

with open('../rawdata/SD_multinomial_PIKK.csv', 'at') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(column_names)
	for i in range(len(result)):
		writer.writerow(result[i])

