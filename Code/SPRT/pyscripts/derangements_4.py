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
column_names = ["prng", "algorithm", "seed", "decision_upper", "LR_upper", "steps_upper",
                 "decision_lower", "LR_lower", "steps_lower"]

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


def sequential_derangement_test(sampling_function, n, alpha, beta, multiplier, maxsteps=10**6):
    '''
    Conduct Wald's SPRT for whether derangements occur more or less frequently than 1/e
    H_0: derangements occur with equal frequency (p approx 1/e)
    H_1 upper: p = p1 = multiplier * p0 > p0
    H_1 lower: p = p1_lower = (2-multiplier) * p0 < p0
    
    sampling_function: a function which generates a random permutation
    n: number of items
    alpha: desired type 1 error rate
    beta: desired type 2 error rate
    multiplier: value in (1, 1/p0). Determines the "greater than" alternative hypothesis,
        and 2-multiplier determines the "less than" alternative hypothesis
    maxsteps: maximum number of trials before stopping the test. Default is 10**6.
    '''

    assert multiplier > 1
    assert maxsteps > 0

    # Set p0 = probability of a derangement
    p0 = prob_derangement(n)
    p1 = multiplier*p0
    p1_lower = (2-multiplier)*p0
    assert p1 < 1
    assert p1_lower < 1
    assert p0 < 1
    
    # Set parameters
    lower = beta/(1-alpha)
    upper = (1-beta)/alpha
    lr_occurs_upper = p1/p0
    lr_doesnotoccur_upper = (1 - p1)/(1 - p0)
    lr_occurs_lower = p1_lower/p0
    lr_doesnotoccur_lower = (1 - p1_lower)/(1 - p0)
    
    LR_upper = [1]
    LR_lower = [1]
    decision_upper = "None"
    decision_lower = "None"      
    vec = np.array(range(0, n))
    steps = 0
    
    lower_test_unfinished = 1
    upper_test_unfinished = 1
    
    # Draw samples
    while steps < maxsteps and (lower_test_unfinished + upper_test_unfinished):
        steps += 1
        perm = sampling_function(n)
        Dn = check_derangement(vec, perm)

        # Run test at step n for greater than alternative
        if upper_test_unfinished:     
            if Dn:
                LR_upper.append(LR_upper[-1] * lr_occurs_upper)
            else:
                LR_upper.append(LR_upper[-1] * lr_doesnotoccur_upper)
            
            if LR_upper[-1] <= lower:
                # accept the null and stop
                decision_upper = 0
                upper_test_unfinished = 0
                
            if LR_upper[-1] >= upper:
                # reject the null and stop
                decision_upper = 1
                upper_test_unfinished = 0 
            
        # Run test at step n for less than alternative
        if lower_test_unfinished:     
            if Dn:
                LR_lower.append(LR_lower[-1] * lr_occurs_lower)
            else:
                LR_lower.append(LR_lower[-1] * lr_doesnotoccur_lower)
            
            if LR_lower[-1] <= lower:
                # accept the null and stop
                decision_lower = 0
                lower_test_unfinished = 0
                
            if LR_lower[-1] >= upper:
                # reject the null and stop
                decision_lower = 1
                lower_test_unfinished = 0       
                
    return {'decision_upper' : decision_upper,
            'decision_lower' : decision_lower,
            'lower_threshold' : lower,
            'upper_threshold' : upper,
            'LR_upper' : LR_upper,
            'LR_lower' : LR_lower,
            'steps_lower' : len(LR_lower)-1,
            'steps_upper' : len(LR_upper)-1
            }
            
            
################################################################################
# Wrapper functions
################################################################################

def testSeed(ss):

    prng = lcgRandom(seed=ss, A=0, B=69069, M=2**32)

    sampling_func = lambda n: fykd(np.array(range(n)), prng)
    res = sequential_derangement_test(sampling_func, n=100, alpha=0.05/2, beta=0, multiplier=1.01)
    return ["SD", "fykd", ss, res['decision_upper'], res['LR_upper'][-1], res['steps_upper'],
            res['decision_lower'], res['LR_lower'][-1], res['steps_lower']]    
    

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
result = lview.map(testSeed, seed_values)

# Write results to file

with open('../rawdata/SD_derangements_fykd_n100.csv', 'at') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(column_names)
	for i in range(len(result)):
		writer.writerow(result[i])

