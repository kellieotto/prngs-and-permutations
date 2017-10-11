import numpy as np
import math
from scipy.stats import chisquare
from scipy.misc import comb
from ipyparallel import Client
from serial_test import serial_perm_distr, test_poisson, compute_bincounts
import csv
sys.path.append('../modules')
from sha256prng import SHA256

# get p-values
np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 1000)
        
        
################################################################################
# Wrapper functions
################################################################################

def testSeed(ss):

    prng = SHA256(ss)
    val = np.array(serial_perm_distr(200, reps=2*10**5, gen=prng), dtype=int)
    bin_counts = compute_bincounts(val)
#    pvalues[pp] = test_poisson(val)
#    res[seed_values[pp]] = bin_counts
    return bin_counts
    
    

def wrapper(i):
    return(testSeed(seed_values[i]))
    
################################################################################
# Set up engines
################################################################################
c = Client(profile="cluster200")
c.ids

dview = c[:]
dview.block = True

lview = c.load_balanced_view()
lview.block = True

dview.execute('import sys')
dview.execute("sys.path.append('../modules')")
dview.execute('from serial_test import serial_perm_distr, test_poisson, compute_bincounts')
dview.execute('from sha256prng import SHA256')
dview.execute('import numpy as np')
mydict = dict(seed_values = seed_values, 
              testSeed = testSeed)
dview.push(mydict)
    

################################################################################
# Execute
################################################################################

# Map it to each seed

#result = list(map(wrapper, range(len(seed_values))))
result = lview.map(lambda ss: testSeed(ss), seed_values)

# Write results to file
with open("sha_fp_distr_200.csv", "w") as f:
    w = csv.writer(f)
    for pp in range(len(pvalues)):
        w.writerow(result[pp])