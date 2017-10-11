import numpy as np
import math
from scipy.stats import chisquare
from scipy.misc import comb
from serial_test import serial_perm_distr, test_poisson, compute_bincounts
import csv

# get p-values
np.random.seed(347728688) # From random.org Timestamp: 2017-01-19 18:22:16 UTC
seed_values = np.random.randint(low = 1, high = 2**32, size = 1000)
pvalues = np.zeros(1000)
res = dict()
for pp in range(1000):
    np.random.seed(seed_values[pp])
    val = np.array(serial_perm_distr(200, reps=2*10**5), dtype=int)
    bin_counts = compute_bincounts(val)
    pvalues[pp] = test_poisson(val)
    res[seed_values[pp]] = bin_counts

np.savetxt("mt_chisq_pvalues_200.txt", pvalues)
with open("mt_fp_distr_200.csv", "w") as f:
    w = csv.writer(f)
    for pp in range(len(pvalues)):
        w.writerow(res[seed_values[pp]].tolist())