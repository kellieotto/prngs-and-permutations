from __future__ import division
import numpy as np


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


def fykd(a, gen=np.random):
    '''
    Fisher-Yates-Knuth-Durstenfeld shuffle: permute a in place
    '''
    for i in range(len(a)-2):
        J = gen.randint(i,len(a))
        a[i], a[J] = a[J], a[i]
    return(a)


def fykd_sample(n, k, gen=np.random):
    '''
    Use fykd to sample k out of 1, ..., n
    '''
    a = list(range(1, n+1))
    a = fykd(a, gen=gen)
    return(a[:k])


def Random_Sample(n, k, gen=np.random):
    '''
    Recursive sampling algorithm from Cormen et al
    '''
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
	
	
def Algorithm_R(n, k, gen=np.random):  
    '''
    Waterman's Algorithm R for resevoir SRSs
    '''
    S = list(range(1, k+1))  # fill the reservoir
    for t in range(k+1,n+1):
        i = gen.randint(1,t+1)
        if i <= k:
            S[i-1] = t
    return set(S)
	
    
def sample_by_index(n, k, gen=np.random):
    '''
    Generate a random sample of 1,...,n by selecting indices uniformly at random
    '''
    nprime = n
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
        
	
def stirling_lower_bound(n):
    return math.sqrt(2*math.pi)*n**(n+.5)*math.e**(-n)


def stirling_lower_bound_log(n):
    return math.log(2*math.pi)/2+(n+.5)*math.log(n)-n*math.log(math.e)


def stirling_upper_bound_log(n):
    return 1+(n+.5)*math.log(n)-n*math.log(math.e)
	
	
def H(p):  # entropy of a Bernoulli(q) variable
    return -p*math.log(p, 2) - (1-p)*math.log(1-p, 2)


def Hcomb(n,k):  # entropy of simple random sampling of k of n 
    # entropy is -\sum p_i \log_2 p_i. Here, all p_i=1/nCk.
    return -math.log(1/comb(n,k), 2)
    

def comb_upper_bound_H(n, k):  # entropy upper bound on nCk
    p = k/n
    return 2**(n*H(p))


def comb_lower_bound_H(n, k): # entropy upper bound on nCk
    p = k/n
    return 2**(n*H(p))/(n+1)


def comb_lower_bound_H_log2(n, k): # entropy upper bound on nCk
    p = k/n
    return n*H(p)-math.log((n+1),2)


def comb_lower_bound_Stirling(l,m): # lower bound on (l^2m)Cl^2
    return m**(m*(l*l-1)+1)/(l*(m-1)**((m-1)*(l*l-1)))