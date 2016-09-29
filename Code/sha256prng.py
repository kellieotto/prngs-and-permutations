"""
To run docstring tests, run the following from the terminal:

python sha256prng.py -v
"""

from __future__ import division
import numpy as np
# Import base class for PRNGs
import random
# Import library of cryptographic hash functions
import hashlib

# Define useful constants
BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF
HASHLEN = 256 # Number of bits in a hash output
RECIP_HASHLEN = 2**-HASHLEN

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


    def seed(self, baseseed=None, counter=0):
        """Initialize internal state from hashable object.

        None or no argument seeds from current time or from an operating
        system specific randomness source if available.

        If a is not None or an int or long, hash(a) is used instead.
		
        a only gets changed at initiation. Counter gets updated each time
        the prng gets called.
        """
        # TODO: how to seed, see Ron's implementation
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
    
    
    def jumpahead(self, n):
        """
        Jump ahead n steps in the period
        """
        self.counter += n        


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
    """
    def random(self, size=None):
        if size==None:
            return self.nextRandom()
        else:
            return np.reshape(np.array([self.nextRandom() for i in np.arange(np.prod(size))]), size)
            
    
    def nextRandom(self):
        hash_input = (str(self.baseseed) + "," + str(self.counter)).encode('utf-8')
        # Apply SHA-256, interpreting hex output as hexadecimal integer
        # to yield 256-bit integer (a python "long integer")
        hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)
        self.next()
        return(hash_output*RECIP_HASHLEN)
        
        
#    def __repr__(self):
        """
        what does this do?
        """
        
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