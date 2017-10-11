import numpy as np
import math
from scipy.stats import chisquare
from scipy.misc import comb


def compute_ev_errors(n):
    ev = 0
    for i in range(1, n+1):
        ev += (i-1)/i
    return ev
    
    
def bayes_est_distr(n, reps=1e5, bayes_order = 'min'):
    """
    Compute the distribution of errors in guessing the permutation using the     following Bayes rule: 
    Given a permutation of (1, 2, ..., n) and a pool of guesses (1, 2, ..., n),     repeat for positions 1 through n-1:
    
    1) Guess that position i of the permutation is the smallest (or largest) value in the     pool
    2) If not a match, add 1 to the error count
    3) Remove the true value of position i from the pool
    
    Inputs
    ------
    n : int
        number of items to permute
    reps : int
        number of times to repeat the procedure, default 1e5
    bayes_order : str
        'min' or 'max': which order should values be guessed? default min.
    """
    
    distr = np.zeros(reps)
    selector = {'min' : min, 'max' : max}
    selector_fun = selector[bayes_order]

    for rr in range(reps):
        pool = list(range(1, n+1))
        perm = pool.copy()
        np.random.shuffle(perm)
        errors = 0
        for i in range(n-1):
            guess = selector_fun(pool)
            truth = perm[i]
            if guess != truth:
                errors += 1
            pool.remove(truth)
        distr[rr] = errors
    
    return distr
	

def bayes_perm_ev(n):
    ev = 0
    for i in range(1, n+1):
        ev += (i-1)/i
    return ev


def serial_perm_distr(n, reps=10**5, gen=np.random, dist = 'equal'):
    """
    Compute the distance between permutations
    
    Inputs
    ------
    n : int
        number of items to permute
    reps : int
        number of times to repeat the procedure, default 1e5
    dist : str
        how to compute distance? 'equal' (default), 'euclidean', 'num_greater'
    """
    
    distr = np.zeros(reps)
    distance = {'equal' : lambda x, y: np.sum((x-y) == 0), 
                'euclidean' : lambda x, y: np.sqrt(np.sum((x-y)**2)),
                'num_greater' : lambda x, y: np.sum((x-y) > 0)}
    distance_fun = distance[dist]
    prev_perm = np.array(range(1, n+1))
	
    for rr in range(reps):
        new_perm = prev_perm.copy()
        gen.shuffle(new_perm)
        measure = distance_fun(new_perm, prev_perm)
        distr[rr] = measure
        prev_perm = new_perm
    
    return distr
	

def count_derangements(n):
    """
    Count the number of derangements of k items, for k=0, 1, ..., n
    """
    derangements = np.ones(n+1)
    derangements[1] = 0
    for i in range(3, n+1):
        derangements[i] = (i-1)*(derangements[i-1] + derangements[i-2])
    return derangements


def fixed_perm_probabilities(n, k):
    """
    Derive the frequency of permutations of n items that fix exactly i items,
    for i = 0, 1, ..., k
    """
    perm_count = np.zeros(k+1)
    derangements = count_derangements(n)
    for i in range(k+1):
        perm_count[i] = derangements[n-i]/(math.factorial(i)*math.factorial(n-i))
    return perm_count


	
def serial_perm_equal_params(n):
    ev = n / math.factorial(n)
    ev2 = n**2 / math.factorial(n)
    for i in range(n-2, 0, -1):
        pmatch = np.prod([1/k for k in range(n, n-i, -1)])
        pfail = 1/(n-i)
        ev += i * comb(n, i) * pmatch * pfail
        ev2 += i**2 * comb(n, i) * pmatch * pfail
    var = ev2 - (ev)**2
    return ev, var
    

def compute_bincounts(distr, nmax = 11):
    ct = np.zeros(nmax+1, dtype=int)
    np_ct = np.bincount(distr)
    if len(np_ct) < nmax+1:
        nn = len(np_ct)
        for i in range(nn):
            ct[i] = np_ct[i]
    else:
        for i in range(nmax):
            ct[i] = np_ct[i]
        ct[nmax] = sum(np_ct[nmax:])
    return ct
    

def test_poisson(distr, nmax=11):
    distr = np.array(distr, dtype=int)
    cell_counts = compute_bincounts(distr, nmax)
    reps = len(distr)
    expected_freq = np.exp(-1)*np.array([1./math.factorial(k) for k in range(nmax)])
    expected_freq = np.append(expected_freq, 1 - np.sum(expected_freq))
    expected_counts = reps*np.array(expected_freq)
    
    res = chisquare(cell_counts, expected_counts)
    return res[1]
    

def test_theoretical(distr, n):
    """
    distr : array-like
        Distribution of matches between serial permutations of n items
    n : int
        length of lists being permuted
    """
    distr = np.array(distr, dtype=int)
    cell_counts = np.bincount(distr)
    nmax = len(cell_counts)
    reps = len(distr)
    
    theoretical_distr = fixed_perm_probabilities(n, nmax)
    expected_counts = theoretical_distr * reps
    if any(expected_counts == 0):
        ind = np.where(expected_counts == 0)
        cell_counts = np.delete(cell_counts, ind)
        expected_counts = np.delete(expected_counts, ind)
    res = chisquare(cell_counts, expected_counts)
    return res[1]