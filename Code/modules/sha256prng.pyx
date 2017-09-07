"""
To run docstring tests, run the following from the terminal:

python sha256prng.py -v
"""

from __future__ import division
import numpy as np
cimport numpy as np
# Import base class for PRNGs
import random
# Import library of cryptographic hash functions
import hashlib
import cython

# Define useful constants
cdef int BPF = 53        # Number of bits in a float
cdef double RECIP_BPF = 2**-BPF
cdef int HASHLEN = 256 # Number of bits in a hash output
cdef double RECIP_HASHLEN = 2.0**-256

################################################################################
############################## Base PRNG Class #################################
################################################################################

class BaseRandom(random.Random):
    '''Random number generator base class'''

    def __init__(self, seed=None):
        """Initialize an instance.

        Optional argument seed controls seeding, as for Random.seed().
        """

        self.seed(seed)


    def seed(self, baseseed=None, int counter=0):
        """Initialize internal state from hashable object.

        None or no argument seeds from current time or from an operating
        system specific randomness source if available.

        If a is not None or an int or long, hash(a) is used instead.
		
        a only gets changed at initiation. Counter gets updated each time
        the prng gets called.
        """
        self.baseseed = baseseed
        self.counter = counter

        
    def next(self):
        """
        Update the counter
        """
        self.counter += 1
        
    
    def getstate(self):
        return (self.baseseed, self.counter)
        
    
    def setstate(self, state):
        """
        Set the state (seed and counter)
        """
        (self.baseseed, self.counter) = (int(val) for val in state)
    
    
    def jumpahead(self, int n):
        """
        Jump ahead n steps in the period
        """
        self.counter += n        

            
    def __repr__(self):
        """
        >>> r = SHA256(5)
        >>> repr(r)
        'SHA256 PRNG with seed 5 and counter 0'
        >>> str(r)
        'SHA256 PRNG with seed 5 and counter 0'
        """
        stringrepr = self.__class__.__name__ + " PRNG with seed " + str(self.baseseed) + " and counter " + str(self.counter)
        return stringrepr
        
        
################################################################################
############################## SHA-256 Class ###################################
################################################################################

class SHA256(BaseRandom):
    """
    PRNG based on the SHA-256 cryptographic hash function.
    
    >>> r = SHA256(5)
    >>> r.getstate()
    (5, 0)
    >>> r.next()
    >>> r.getstate()
    (5, 1)
    >>> r.jumpahead(5)
    >>> r.getstate()
    (5, 6)
    >>> r.seed(22, 3)
    >>> r.getstate()
    (22, 3)
    >>> r.hashfun
    'SHA-256'
    >>> r.basehash.__class__.__name__
    'HASH'
    """
    
    def __init__(self, seed=None):
        self.seed(seed)
        self.hashfun = "SHA-256"
        self._basehash()


    def _basehash(self):
        if self.baseseed is not None:
            hashinput = (str(self.baseseed) + ',').encode()
            self.basehash = hashlib.sha256(hashinput)
        else:
            self.basehash = None


    def seed(self, baseseed=None, int counter=0):
        """Initialize internal state from hashable object.

        None or no argument seeds from current time or from an operating
        system specific randomness source if available.

        If a is not None or an int or long, hash(a) is used instead.
		
        a only gets changed at initiation. Counter gets updated each time
        the prng gets called.
        """
        if not hasattr(self, 'baseseed') or baseseed != self.baseseed:    
            self.baseseed = baseseed
            self._basehash()    
        self.counter = counter


    def setstate(self, state):
        """
        Set the state (seed and counter)
        """
        (self.baseseed, self.counter) = (int(val) for val in state)
        self._basehash()


    def random(self, size=1):
        """
        Generate random numbers between 0 and 1.
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.

        >>> r = SHA256(12345678901234567890)
        >>> r.next()
        >>> e1 = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
        >>> e2 = int("ae230ec16bee77f77c7378f4eb5d265d931665e29e8bbee7e733f58d3815d338", 16)
        >>> expected = np.array([e1, e2]) * 2**-256
        >>> r.random(2) == expected
        array([ True,  True], dtype=bool)
        """
        cdef int i
        cdef int size2 = np.prod(size)
        cdef np.ndarray[double, ndim=1] res = np.empty(size2, dtype=np.float)
        
        if size==1:
            return self.nextRandom()*RECIP_HASHLEN
        else:
            for i in range(size2):
                res[i] = self.nextRandom()*RECIP_HASHLEN
            return np.reshape(res, size)
            
    
    def nextRandom(self):
        """
        Generate the next hash value
        
        >>> r = SHA256(12345678901234567890)
        >>> r.next()
        >>> expected = int("4da594a8ab6064d666eab2bdf20cb4480e819e0c3102ca353de57caae1d11fd1", 16)
        >>> r.nextRandom() == expected
        True
        """
        hashfun = self.basehash.copy()
        hashfun.update(str(self.counter).encode())
        # Apply SHA-256, interpreting hex output as hexadecimal integer
        # to yield 256-bit integer (a python "long integer")
        hash_output = int(hashfun.hexdigest(),16)
        self.next()
        return(hash_output)


    def randint(self, int a, int b, size=1):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        The following tests match the output of Ron's and Philip's implementations.

        >>> r = SHA256(12345678901234567890)
        >>> r.randint(1, 1000, 5)
        array([ 86, 248, 969, 467, 708])
        """
        cdef int i
        cdef int size2 = np.prod(size)
        cdef np.ndarray[np.int32_t, ndim=1] res = np.empty(size2, dtype=np.int32)
        
        assert a <= b, "lower and upper limits are switched"
        
        if size==1:
            return a + (self.nextRandom() % (b-a))
        else:
            for i in range(size2):
                res[i]= a + (self.nextRandom() % (b-a))
            return np.reshape(res, size)

        
        
################################################################################
############################## some sample code ################################
################################################################################

# pseudo-random number generator
def toy_example():
    seed = 12345678901234567890
    count = 0
    hash_input = (str(seed) + "," + str(count)).encode('utf-8')
    # Apply SHA-256, interpreting hex output as hexadecimal integer
    # to yield 256-bit integer (a python "long integer")
    hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)

    print(hash_output*RECIP_HASHLEN)
    count += 1


if __name__ == "__main__":
    import doctest
    doctest.testmod()