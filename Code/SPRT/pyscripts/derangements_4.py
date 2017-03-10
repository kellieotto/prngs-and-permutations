################################################################################
# SLURM Array Job 4
# SPRT of permutation derangements, SD, n=100, fykd
################################################################################

import numpy as np
import csv
from ipyparallel import Client
import os

import sys
sys.path.append('../../modules')
from sample import permute_indices, fykd
from prng import lcgRandom

np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 1000)
column_names = ["prng", "algorithm", "seed", "decision", "LR", "pvalue", "steps"]

################################################################################
# SPRT functions
################################################################################

def prob_derangement(n):
    fp_prob = np.ones(n+1)
    for k in range(1, len(fp_prob)):
        fp_prob[k] = -1/k
    fp_prob = np.cumprod(fp_prob)
    return sum(fp_prob)
    

def check_derangement(vec, perm):
    '''
    Check whether perm is a derangement of vec
    Inputs must be numpy arrays
    '''
    
    return not any(np.equal(vec, perm))


def sequential_derangement_test(sampling_function, n, alpha, beta, multiplier, maxsteps=10**7):
    '''
    Conduct Wald's SPRT for whether derangements occur more or less frequently than 1/e
    H_0: derangements occur with equal frequency (p approx 1/e)
    H_1: p = p1 = multiplier * p0, multiplier in the range (0, 1/p0)
    
    sampling_function: a function which generates a random permutation
    n: number of items
    alpha: desired type 1 error rate
    beta: desired type 2 error rate
    multiplier: value in (0, 1/p0). Determines alternative hypothesis
    maxsteps: maximum number of trials before stopping the test. Default is 10**8.
    '''

    assert maxsteps > 0

    # Set p0 = probability of a derangement
    p0 = prob_derangement(n)
    p1 = multiplier*p0
    
    # Set parameters
    lower = beta/(1-alpha)
    upper = (1-beta)/alpha
    lr_occurs = p1/p0
    lr_doesnotoccur = (1 - p1)/(1 - p0)

    LR = [1]
    decision = 'None'        
    vec = np.array(range(0, n))
    steps = 0
    
    # Draw samples
    while lower < LR[-1] < upper and steps < maxsteps:
        steps += 1
        perm = sampling_function(n)
        Dn = check_derangement(vec, perm)

        if Dn:
            LR.append(LR[-1] * lr_occurs)
        else:
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

def testSeed(ss):

    prng = lcgRandom(seed=ss, A=0, B=69069, M=2**32)

    sampling_func = lambda n: fykd(np.array(range(n)), prng)
    res = sequential_derangement_test(sampling_func, n=100, alpha=0.05, beta=0, multiplier=1.1)
    return ["SD", "fykd", ss, res['decision'], res['LR'][-1], res['pvalue'], res['steps']]
    
    

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
dview.execute('from sample import permute_indices, fykd')
dview.execute('from prng import lcgRandom')
dview.execute('from scipy.misc import comb')
dview.execute('import numpy as np')
mydict = dict(seed_values = seed_values, 
              testSeed = testSeed,
              prob_derangement = prob_derangement,
              check_derangement = check_derangement,
              sequential_derangement_test = sequential_derangement_test)
dview.push(mydict)

################################################################################
# Execute
################################################################################

# Map it to each seed

#result = list(map(wrapper, range(len(seed_values))))
result = lview.map(testSeed, seed_values))

# Write results to file

with open('../rawdata/SD_derangements_fykd_n100.csv', 'at') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(column_names)
	for i in range(len(result)):
		writer.writerow(result[i])

