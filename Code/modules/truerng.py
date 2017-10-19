"""
To run docstring tests, run the following from the terminal:

python truerng.py -v
"""

from __future__ import division
import numpy as np
from nistbeacon import NistBeacon
import quantumrandom
import requests
import random
import os

# Define useful constants
BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF
BPI = 16 # Bits per integer
RECIP_BPI = 2**-BPI
BITLEN = 512 # Number of bits in a hash output
RECIP_BITLEN = 2**-BITLEN
DATA_PATH = os.path.join(os.path.dirname(__file__), "truerng-bytes")

################################################################################
############################# NIST RNG Class ###################################
################################################################################

# https://www.nist.gov/programs-projects/nist-randomness-beacon

class NistBeaconRandom(random.Random):
    '''Random number generator base class'''

    def __init__(self, seed=None):
        """Initialize an instance.
        """
        if seed == None:
            self.timestamp = 1378395540 # this is the first possible timestamp
        else:
            self.timestamp = seed
        self.beacon = NistBeacon()


    def get_value(self):
        """
        Get a random number from the server
        """
        val = self.beacon.get_record(self.timestamp).output_value
        return int(val,16)
    
    
    def next(self):
        """
        Update the counter
        """
        self.timestamp += 60 # 60 seconds = 1 step
        
    
    def getstate(self):
        return (self.timestamp)
    
    
    def jumpahead(self, n):
        """
        Jump ahead n steps in time
        """
        self.timestamp += n*60
        self.get_value()

            
    def __repr__(self):
        """
        >>> r = true_random()
        >>> repr(r)
        'True RNG with Timestamp 0'
        >>> str(r)
        'True RNG with Timestamp 0'
        """
        stringrepr = "True RNG with Timestamp " + str(self.timestamp)
        return stringrepr
        
        
    def random(self, size=None):
        """
        Generate random numbers between 0 and 1.
        size controls the number of ints generated. If size=None, just one is produced.
        """
        if size==None:
            return self.nextRandom()*RECIP_BITLEN
        else:
            return np.reshape(np.array([self.nextRandom()*RECIP_BITLEN for i in np.arange(np.prod(size))]), size)
            
            
    def nextRandom(self):
        """
        Generate the next random number
        """
        val = self.get_value()
        self.next()
        return(val)


    def randint(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        """
        assert a <= b, "lower and upper limits are switched"
        
        if size==None:
            return a + (self.nextRandom() % (b-a))
        else:
            return np.reshape(np.array([a + (self.nextRandom() % (b-a)) for i in np.arange(np.prod(size))]), size)        
            
            



################################################################################
############################ Quantum RNG Class #################################
################################################################################

class quantumRandom(random.Random):
    '''Random number generator base class'''

    def __init__(self):
        """Initialize an instance.
        """
        self.counter = 0
        self.get_values()

    def get_values(self):
        """
        Get an array of 1000 random numbers from the server
        """
        self.rns = quantumrandom.get_data(data_type='uint16', array_length=1000)


    def renew_values(self):
        if self.counter >= 1000:
            self.counter = self.counter % 1000
            self.get_values()
    
    
    def next(self):
        """
        Update the counter
        """
        self.counter += 1
        self.renew_values()
        
    
    def getstate(self):
        return (self.counter)
    
    
    def jumpahead(self, n):
        """
        Jump ahead n steps in the period
        """
        self.counter += n
        self.renew_values()

            
    def __repr__(self):
        """
        >>> r = true_random()
        >>> repr(r)
        'True RNG with counter 0'
        >>> str(r)
        'True RNG with counter 0'
        """
        stringrepr = "True RNG with counter " + str(self.counter)
        return stringrepr
        
        
    def random(self, size=None):
        """
        Generate random numbers between 0 and 1.
        size controls the number of ints generated. If size=None, just one is produced.
        """
        if size==None:
            return self.nextRandom()*RECIP_BPI
        else:
            return np.reshape(np.array([self.nextRandom()*RECIP_BPI for i in np.arange(np.prod(size))]), size)
            
            
    def nextRandom(self):
        """
        Generate the next random number
        """
        val = self.rns[self.counter]
        self.next()
        return(val)


    def randint(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        """
        assert a <= b, "lower and upper limits are switched"
        
        if size==None:
            return a + (self.nextRandom() % (b-a))
        else:
            return np.reshape(np.array([a + (self.nextRandom() % (b-a)) for i in np.arange(np.prod(size))]), size)
            
            
################################################################################
########################## Read RNGs from file #################################
################################################################################

class TrueRandom(random.Random):
    '''Random number generator base class'''

    def __init__(self, seed=None, counter=0):
        """Initialize an instance.
        """
        self.counter = counter
        if seed == None:
            self.seed = 0 # this is the first possible timestamp
        else:
            self.seed = seed
        try:
            fname = os.path.join(DATA_PATH, "block" + str(self.seed) + ".rng")
            self.file = open(fname, "rb")
        except ValueError:
           print("Bad seed -- file with that number does not exist")
    
    def next(self):
        """
        Update the counter
        """
        self.counter += 1


    def getstate(self):
        return (self.seed, self.counter)


    def jumpahead(self, n):
        """
        Jump ahead n steps
        """
        self.counter += n
        self.file.read(n)
            
    def __repr__(self):
        """
        >>> r = TrueRandom()
        >>> repr(r)
        'True RNG from file block0.rng'
        >>> str(r)
        'True RNG from file block0.rng'
        """
        stringrepr = "True RNG from file block" + str(self.seed) + ".rng"
        return stringrepr
        
        
    def random(self, size=None):
        """
        Generate random numbers between 0 and 1.
        size controls the number of ints generated. If size=None, just one is produced.
        """
        if size==None:
            return self.nextRandom()*RECIP_BPI
        else:
            return np.reshape(np.array([self.nextRandom()*RECIP_BPI for i in np.arange(np.prod(size))]), size)
            
            
    def nextRandom(self):
        """
        Generate the next random number
        """
        val = self.file.read(2)
        self.next()
        return (val[0])*2**8 + (val[1])


    def randint(self, a, b, size=None):
        """
        Generate random integers between a (inclusive) and b (exclusive).
        size controls the number of ints generated. If size=None, just one is produced.
        """
        assert a <= b, "lower and upper limits are switched"
        
        if size==None:
            return a + (self.nextRandom() % (b-a))
        else:
            return np.reshape(np.array([a + (self.nextRandom() % (b-a)) for i in np.arange(np.prod(size))]), size)
            
    
    def finish(self):
        self.file.close()
            
            
