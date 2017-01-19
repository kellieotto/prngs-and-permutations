import math
from scipy.stats import itemfreq, chisquare, kstest, norm, triang
from scipy.misc import comb
import scipy.integrate as integrate
import numpy as np
import pandas as pd


def conductChisqTest(sequence, multiplier=2**10):
    '''
    Given a sequence of U(0,1) values, bin values by scaling by multiplier and taking the floor.
    Then conduct a chi-squared test for uniformity on these categories.
    
    Returns the p-value.
    '''
    
    bins = [int(np.floor(val*multiplier)) for val in sequence]
    res = chisquare(itemfreq(bins)[:,1])
    return(res[1])
    
      
def distrNormalRange(w, n):
    '''
    The CDF of the range of n IID standard normals evaluated at w
    '''
    innerInt = lambda x: norm.pdf(x)*(norm.cdf(x+w) - norm.cdf(x))**(n-1)
    tmp = integrate.quad(innerInt, -2*w, 2*w)
    if n*tmp[0] > 1:
        return n*(tmp[0] - tmp[1])
    else:
        return n*tmp[0]


def distrMultinomialRange(w, n, k):
    '''
    CDF of the range of multinomial variables, evaluated at w
    n draws, k categories each having probability 1/k
    '''
    cutoff = (w - 1/(2*n))*np.sqrt(k/n)
    return distrNormalRange(cutoff, k)


def conductRangeTest(sequence, multiplier=2**10):
    '''
    Given a sequence of U(0,1) values, bin values by scaling by multiplier and taking the floor.
    Then conduct a test for uniformity on these categories using the range of bin counts.
    
    Returns the p-value.
    '''
    
    bins = [int(np.floor(val*multiplier)) for val in sequence]
    counts = itemfreq(bins)[:,1]
    return 1 - distrMultinomialRange(np.ptp(counts), np.sum(counts), len(counts))
    
    
def conductKSTest(sequence, null_distribution='uniform'):
    '''
    Given a sequence of values conduct a one-sample Kolmogorov-Smirnov test comparing the
    observed sequence to a null distribution. By default, the null is the uniform
    distribution on [0,1].
    
    sequence: array or list
        a list of values from an empirical distribution
    null_distribution: str or callable (default is 'uniform')
        If a string, it should be the name of a distribution in scipy.stats.
        If a callable, that callable is used to calculate the cdf.
    
    Returns the two-sided p-value.
    '''
    
    return kstest(sequence, null_distribution)[1]
    
    
def conductGapTest(sequence, alpha, beta, t):
    '''
    Given a sequence of values, conduct the gap test. Gaps are defined to be the number of 
    observations r where X_j and X_{j+r-1} fall in the range [alpha, beta), 
    but X_{j+1}, ..., X_{j+r-2} do not.
    
    Input
    ----
    sequence: list or array
        sequence of numbers between 0 and 1
    alpha: float
        lower limit of interval, must be at least 0
    beta: float
        upper limit of interval, must be at most 1
    t: int
        max gap size (anything with gap larger than t will fall in the last category)
    
    Returns a dict
    --------------
    observed: list
        number of gaps of length 0, 1, ..., >=t
    expected: list
        expected number of gaps of length 0, 1, ..., >=t conditional on the total number
        of observed gaps
    p-value: float
        p-value of the chi-squared test comparing observed and expected counts
    
    '''
    # check
    assert alpha >= 0
    assert beta <= 1
    assert alpha < beta
    
    # initialize
    count = [0 for r in range(t+1)]
    r = 0
    n = len(sequence)
    
    # count gaps of size 0, 1, ..., >=t
    for j in range(n):
        if sequence[j] >= alpha and sequence[j] < beta:
            if r >= t:
                count[t] += 1
            else:
                count[r] += 1
            r = 0
        else:
            r += 1
            
    # conduct chi-square test
    p = beta-alpha
    conditional_n = sum(count)
    expected = [conditional_n*p*(1-p)**power for power in range(t)]
    expected.append(conditional_n*(1-p)**t)
    return {'observed' :  count,
            'expected' : expected,
            'p-value' : chisquare(count, expected)[1]}
            
            
def conductPermTest(sequence, tuplelen):
    '''
    Given a sequence of U(0,1) values, break sequence into tuples of length tuplelen. 
    Find the ordering of each tuple, and do a chi-squared test.
    Under the null, each ordering has equal probability.
        
    Returns the p-value.
    '''
    
    nperms = np.floor(len(sequence)/tuplelen)
    counts = dict()
    
    for j in range(int(nperms)):
        f = str(np.argsort(sequence[(j*tuplelen):(j*tuplelen + tuplelen )]))
        if f in counts.keys():
            counts[f] += 1
        else:
            counts[f] = 1
    return chisquare(list(counts.values()))[1]
    
    
def conduct_sample_by_index_test(sequence, n, k):
    '''
    Given a sequence of values, test how uniformly the sample_by_index algorithm way of
    generating integers is able to produce sequences of random ints when taking this sequence
    as the stream of random numbers.
    
    Given ints n>k, sample_by_index samples uniformly at random from {1, ..., n},
    then from {1, ..., n-1}, down to {1, ..., n-k+1} at the last step. The samples
    produced in this way should occur with equal frequency.
    
    Conduct a chi-squared test to test this.
    
    Input
    ----
    sequence: list or array
        sequence of numbers between 0 and 1
    n: int
        "population" size
    k: int
        "sample" size, less than n
    
    Returns a dict
    --------------
    count: dict
        Keys are each sample and values are the number of times it occurred
    p-value: float
        p-value of the chi-squared test comparing observed and expected counts
    
    '''
    nprime = n
    j = 0
    samp = []
    counts = dict()
    
    for j in range(len(sequence)):
        if nprime > n-k:
            samp.append( np.floor(nprime * sequence[j]) )
            nprime -= 1
        else:
            f = str(samp)
            if f in counts.keys():
                counts[f] += 1
            else:
                counts[f] = 1
            nprime = n
            samp = []

    return {'counts' : counts,
            'p-value' : chisquare(list(counts.values()))[1]}