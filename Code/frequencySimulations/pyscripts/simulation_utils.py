from __future__ import division
import numpy as np
from scipy.misc import comb, factorial
from scipy.stats import chisquare, norm 
import scipy.integrate as integrate
import pandas as pd

import sys
sys.path.append('../../modules')
from prng import lcgRandom
from sample import PIKK

def getEmpiricalDistr(randomObject, n, k, reps=10**7):
    uniqueSamples = dict()

    for i in range(reps): # use range in python 3, xrange in python 2
        sam = frozenset(PIKK(n, k, randomObject))
        if sam in uniqueSamples:
            uniqueSamples[sam] += 1
        else:
            uniqueSamples[sam] = 1
    return uniqueSamples
    

def getItemCounts(uniqueSamples):
    itemCounts = dict()
    for u,v in uniqueSamples.items():
        for i in u:
            if i in itemCounts:
                itemCounts[i] += v
            else:
                itemCounts[i] = v
    return itemCounts


def printItemFreq(itemCounts, reps, verbose=False):
    for i in itemCounts.keys():
        itemCounts[i] /= reps
        if verbose:
            print(i, itemCounts[i])
    return itemCounts
    

def printMaxProbRatio(itemCounts, verbose=False):
    freq = list(itemCounts.values())
    pr = np.amax(freq)/np.amin(freq)
    if verbose:
        print("Max ratio of selection probs: " + str(pr))
    return pr


def conductChiSquareTest(itemCounts):
    freq = list(itemCounts.values())
    return(chisquare(freq))
    
    
def distrNormalRange(w, n):
    '''
    The CDF of the range of n IID standard normals evaluated at w
    '''
    innerInt = lambda x: norm.pdf(x)*(norm.cdf(x+w) - norm.cdf(x))**(n-1)
    tmp = integrate.quad(innerInt, -2*w, 2*w)
    return n*(tmp[0] - tmp[1])


def test_distrNormalRange():
    n = 100
    np.random.seed(12345)

    empiricalRangeDistr = np.array([np.ptp(norm.rvs(size=n)) for i in range(100000)])
    for w in np.array(range(6,13))/2:
        emp = np.mean(empiricalRangeDistr <= w)
        theoretical = distrNormalRange(w, n)
        assert np.abs(emp - theoretical) <= 0.005
    return None


def distrMultinomialRange(w, n, k):
    '''
    CDF of the range of multinomial variables, evaluated at w
    n draws, k categories each having probability 1/k
    '''
    cutoff = (w - 1/(2*n))*np.sqrt(k/n)
    return distrNormalRange(cutoff, k)


def test_distrMultinomialRange():
    reps = 10000
    bins = 15
    np.random.seed(12345)

    empiricalRangeDistr = np.ptp(np.random.multinomial(n=reps, pvals=[1/bins]*bins, size=100000), axis=1)
    for w in np.array(range(20))*10:
        emp = np.mean(empiricalRangeDistr <= w)
        theoretical = distrMultinomialRange(w, reps, bins)
        assert np.abs(emp - theoretical) <= 0.05
    return None

# will be silent if there are no errors
test_distrNormalRange()
test_distrMultinomialRange()

def findFreqItems(itemCounts, m):
    '''
    Return indices of the m most frequently occurring items
    '''
    ordered = sorted(enumerate(list(itemCounts.values())), key = lambda x: x[1], reverse = True)
    topM = ordered[:m]
    grabIndex = [i[0] for i in topM]
    return grabIndex


def getPopMean(x):
    return(np.mean(x))


def getSampleMean(x, uniqueSamples):
    m = 0
    totCnt = 0
    for sam, cnt in uniqueSamples.items():
        m += np.mean([x[i] for i in sam])*cnt
        totCnt += cnt
    sampleMean = m/totCnt
    return(sampleMean)

    
def makePopulation(n, p):
    '''
    Create a population of 0s and 1s
    n = pop size
    p = number of 1s in the population
    '''
    x = [0]*n
    x[:p] = [1]*p
    return(x)


def makeAdversarialPopulation(n, indices):
    '''
    Create a population of 0s and 1s
    n = pop size
    indices = locations to put the 1s
    '''
    x = [0]*n
    for i in indices:
        x[i] = 1
    return x