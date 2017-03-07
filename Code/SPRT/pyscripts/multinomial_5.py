################################################################################
# SLURM Array Job 5
# SPRT of sample probabilities (multinomial equal p), SHA256, n=13, k=3, s = 10, PIKK
################################################################################

import numpy as np
import csv
from scipy.misc import comb
from ipyparallel import Client
import os

import sys
sys.path.append('../../modules')
from sample import PIKK, sample_by_index
from sha256prng import SHA256

np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 1000)
column_names = ["prng", "algorithm", "seed", "decision", "LR", "pvalue", "steps", "n", "k", "s"]

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
        s = math.ceil(0.01*num_categories)
    assert isinstance(s, int)    


    k = num_categories # Rename for ease of use!
    
    # Set p0 = s/k, p1 = multiplier*(s/k)
    p0 = s/k
    p1 = multiplier*s/k
    assert p1 < 1
    assert p0 < 1
    
    # Set parameters
    lower = beta/(1-alpha)
    upper = (1-beta)/alpha
    lr_occurs = p1/p0
    lr_doesnotoccur = (1 - p1)/(1 - p0)

    # Initialize counter
    sampleCounts = dict()
    while len(sampleCounts.keys()) < s:
        Xn = str(sorted(sampling_function()))
        if Xn not in sampleCounts.keys():
            sampleCounts[Xn] = 0
    steps = 0
    LR = [1]
    decision = "None"        
    
    # Draw samples
    while lower < LR[-1] < upper and steps < maxsteps:
        Xn = str(sorted(sampling_function()))

        # Event occurs if Xn is among the top s most frequent values of X1,...,X_n-1
        steps += 1
        top_categories = sorted(sampleCounts, key = sampleCounts.get, reverse = True)[:s]
        if Xn in top_categories:
            Bn = 1
            LR.append(LR[-1] * lr_occurs)
        else:
            Bn = 0
            LR.append(LR[-1] * lr_doesnotoccur)

        # Run test at step n
        if LR[-1] <= lower:
            # accept the null and stop
            decision = 0
            break
        if LR[-1] >= upper:
            # reject the null and stop
            decision = 1
            break
        
        # add Xn to sampleCounts and repeat
        if Xn in sampleCounts.keys():
            sampleCounts[Xn] += 1
        else:
            sampleCounts[Xn] = 1
    return {'decision' : decision,
            'lower' : lower,
            'LR' : LR,
            'upper' : upper,
            'steps' : steps,
            'pvalue' : min(1/LR[-1], 1)
            }
            
            
################################################################################
# Wrapper functions
################################################################################

def testSeed(ss, n, k, s):

    prng = SHA256(ss)
    
    sampling_func = lambda: PIKK(n, k, prng)
    res = sequential_multinomial_test(sampling_func, num_categories=comb(n, k), alpha=0.05, beta=0, multiplier=1.1, s=s)
    return ["SHA256", "PIKK", ss, res['decision'], res['LR'][-1], res['pvalue'], res['steps'], n, k, s]
    
    

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
dview.execute('from scipy.misc import comb')
dview.execute('import numpy as np')
mydict = dict(seed_values = seed_values, 
              testSeed = testSeed,
              sequential_multinomial_test = sequential_multinomial_test)
dview.push(mydict)
    

################################################################################
# Execute
################################################################################

# Map it to each seed

#result = list(map(wrapper, range(len(seed_values))))
result = lview.map(lambda ss: testSeed(ss, n=13, k=3, s=10), seed_values)


# Write results to file

with open('../rawdata/SHA256_multinomial_PIKK.csv', 'at') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(column_names)
	for i in range(len(result)):
		writer.writerow(result[i])

