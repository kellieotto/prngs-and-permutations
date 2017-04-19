################################################################################
# SLURM Array Job 1
# Conditional SPRT of sample probabilities (multinomial equal p), MT, n=13, k=3, s = (5,10,20), PIKK
################################################################################

import numpy as np
import csv
from scipy.misc import comb
from ipyparallel import Client
import os

import sys
sys.path.append('../../modules')
from sample import PIKK, sample_by_index

np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 100)
s = [5, 10, 20]
column_names = ["prng", "algorithm", "seed", "n", "k"]
for ss in s:
    column_names.append("decision_s" + str(ss))
    column_names.append("LR_s" + str(ss))
    column_names.append("steps_s" + str(ss))
    column_names.append("top_s_occurs" + str(ss))

################################################################################
# SPRT functions
################################################################################

def sequential_multinomial_conditional_test(sampling_function, alpha, beta, multiplier, \
                                s, maxsteps=10**8):
    '''
    Conduct Wald's SPRT for multinomial distribution, conditional on samples being in the
    top or bottom s most frequent categories
    H_0: selection probabilities are all 1/num_categories so p=s/num_categories
    H_1: probability of landing in top s is higher than landing in lowest s
    
    sampling_function: a function which generates a random number or random sample.
    alpha: desired type 1 error rate
    beta: desired power
    multiplier: value larger than 1. Determines alternative: p1 = multiplier/2
    s: tuning parameter, number of top + bottom categories considered. An integer between 1 and k.
    maxsteps: max number of samples before the algorithm terminates.
    '''

    assert multiplier > 1
    assert maxsteps > 0
    if isinstance(s, int):
        s = [s]
    
    # Set parameters
    lower = beta/(1-alpha)
    upper = (1-beta)/alpha

    # Initialize counter
    sampleCounts = dict()
    while len(sampleCounts.keys()) < 2*max(s):
        Xn = str(sorted(sampling_function()))
        if Xn not in sampleCounts.keys():
            sampleCounts[Xn] = 0
    steps = 0
    event_occurs = {ss: 0 for ss in s}
    top_s_occurs = {ss: 0 for ss in s}
    LR = {ss: [1] for ss in s}
    decision = {ss: "None" for ss in s}
    num_steps = {ss: maxsteps for ss in s}
    tests_running = len(s)
    
    # Draw samples
    while tests_running and steps < maxsteps:
        Xn = str(sorted(sampling_function()))
        top_categories = sorted(sampleCounts, key = sampleCounts.get, reverse = True)

        # add Xn to sampleCounts and repeat
        if Xn in sampleCounts.keys():
            sampleCounts[Xn] += 1
        else:
            sampleCounts[Xn] = 1

        steps += 1    
        for ss in s:
            # Run test for greater than alternative
            # Event occurs if Xn is among the s most frequent values of X1,...,X_n-1
            if (Xn not in top_categories[:ss]) and (Xn not in top_categories[-ss:]):
                continue
            event_occurs[ss] += 1
            
            if Xn in top_categories[:ss]:
                top_s_occurs[ss] += 1
                LR[ss].append(LR[ss][-1] * multiplier) # p1/p0 = multiplier
            else:
                LR[ss].append(LR[ss][-1] * (1 - multiplier/2)*2) # (1-p1)/(1-p0)

            # Run test at step n
            if LR[ss][-1] <= lower:
                # accept the null and stop
                decision[ss] = 0
                num_steps[ss] = steps
                tests_running -= 1
                s.remove(ss)
                
            if LR[ss][-1] >= upper:
                # reject the null and stop
                decision[ss] = 1
                num_steps[ss] = steps
                tests_running -= 1
                s.remove(ss)


    return {'decision' : decision,
            'lower_threshold' : lower,
            'LR' : LR,
            'upper_threshold' : upper,
            'steps' : num_steps,
            'event_occurs' : event_occurs,
            'top_s_occurs' : top_s_occurs
            }
            
################################################################################
# Wrapper functions
################################################################################

def testSeed(ss, n, k, s):

    prng = np.random
    prng.seed(ss)
    
    sampling_func = lambda: PIKK(n, k, prng)
    res = sequential_multinomial_conditional_test(sampling_func, alpha=0.05, beta=0, multiplier=1.01, s=s)

    unpack = ["MT", "PIKK", ss, n, k]
    for svalue in s:
        unpack.append(res['decision'][svalue])
        unpack.append(res['LR'][svalue][-1])
        unpack.append(res['event_occurs'][svalue])
        unpack.append(res['top_s_occurs'][svalue])
    return unpack
    
    

def wrapper(i):
    return(testSeed(seed_values[i], n=13, k=3, s=s))
    
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
              sequential_multinomial_conditional_test = sequential_multinomial_conditional_test,
              s = s)
dview.push(mydict)


################################################################################
# Execute
################################################################################

# Map it to each seed

#result = list(map(wrapper, range(len(seed_values))))
result = lview.map(wrapper, range(len(seed_values)))

# Write results to file

with open('../rawdata/MT_multinomial_condit_PIKK.csv', 'at') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(column_names)
	for i in range(len(result)):
		writer.writerow(result[i])

