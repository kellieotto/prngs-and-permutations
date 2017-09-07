from __future__ import division
import numpy as np
cimport numpy as np
import cython


def PIKK(n, k, gen=np.random):
    '''
    PIKK Algorithm: permute indices and keep k
    '''
    return set(np.argsort(gen.random(n))[0:k])
	


def permute_indices(n, gen=np.random):
    '''
    PIKK algorithm, but we keep all n
    '''
    return np.argsort(gen.random(n))


def fykd_slow(a, gen=np.random):
    '''
    Fisher-Yates-Knuth-Durstenfeld shuffle: permute a in place
    '''
    cdef int i, J
    for i in range(len(a)-1):
        J = gen.randint(i,len(a))
        a[i], a[J] = a[J], a[i]
    return(a)


def fykd(a, gen=np.random):
    '''
    Fisher-Yates-Knuth-Durstenfeld shuffle: permute a in place
    '''
    cdef int n = len(a)
    cdef int i, J
    cdef np.ndarray[double] rand = gen.random(n-1)
    cdef np.ndarray[np.int64_t, ndim=1] ind = np.array(range(n-1), dtype=np.int64)
    JJ = np.array(ind + rand*(n - ind), dtype = int)
    for i in range(n-1):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return(a)


def fykd_sample(int n, int k, gen=np.random):
    '''
    Use fykd to sample k out of 1, ..., n
    '''
    cdef int i, J
    cdef np.ndarray[np.int64_t] a = np.array(range(1, n+1), dtype=np.int64)
    cdef np.ndarray[double] rand = gen.random(k)
    cdef np.ndarray[np.int64_t] ind = np.array(range(k), dtype=np.int64)
    JJ = np.array(ind + rand*(n - ind), dtype = int)
    for i in range(k):
        J = JJ[i]
        a[i], a[J] = a[J], a[i]
    return(a[:k])


def Random_Sample(int n, int k, gen=np.random):
    '''
    Recursive sampling algorithm from Cormen et al
    '''
    cdef int i
    if k==0:
        return set()
    else:
        S = Random_Sample(n-1, k-1)
        i = gen.randint(1,n+1) 
        if i in S:
            S = S.union([n])
        else:
            S = S.union([i])
    return S
	
	
def Algorithm_R(int n, int k, gen=np.random):  
    '''
    Waterman's Algorithm R for resevoir SRSs
    '''
    cdef int t
    S = list(range(1, k+1))  # fill the reservoir
    for t in range(k+1,n+1):
        i = gen.randint(1,t+1)
        if i <= k:
            S[i-1] = t
    return set(S)
	
    
def sample_by_index(int n, int k, gen=np.random):
    '''
    Generate a random sample of 1,...,n by selecting indices uniformly at random
    '''
    cdef int nprime = n
    cdef int j, w
    S = set()
    Pop = list(range(1, n+1))
    while nprime > n-k:
        w = gen.randint(1, nprime+1)
        j = Pop[w-1]
        S = S.union([j])
        lastvalue = Pop.pop()
        if w < nprime:
            Pop[w-1] = lastvalue # Move last population item to the wth position
        nprime = nprime - 1
    return set(S)
