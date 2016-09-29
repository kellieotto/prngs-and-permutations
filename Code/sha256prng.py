from __future__ import division
# Import base class for PRNGs
import random
# Import library of cryptographic hash functions
import hashlib

# Define useful constants
BPF = 53        # Number of bits in a float
RECIP_BPF = 2**-BPF
HASHLEN = 256 # Number of bits in a hash output
RECIP_HASHLEN = 2**-HASHLEN

class MyRandom(random.Random):
    '''Random number generator base class'''

    def __init__(self, x=None):
        """Initialize an instance.

        Optional argument x controls seeding, as for Random.seed().
        """

        self.seed(x)
        self.next = None


    def seed(self, a=None, counter=0):
        """Initialize internal state from hashable object.

        None or no argument seeds from current time or from an operating
        system specific randomness source if available.

        If a is not None or an int or long, hash(a) is used instead.
		
        a only gets changed at initiation. Counter gets updated each time
        the prng gets called.
        """
        # TODO: how to seed, see Ron's implementation
        self.seedv = a
        self.count = counter
        
    
    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        hash_input = (str(self.seedv) + "," + str(self.count)).encode('utf-8')
        # Apply SHA-256, interpreting hex output as hexadecimal integer
        # to yield 256-bit integer (a python "long integer")
        hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)
        return(hash_output*RECIP_HASHLEN)


	def getstate():
        """Return internal state; can be passed to setstate() later."""
        return self.VERSION, super(Random, self).getstate(), self.gauss_next
	    # TODO: does this need to be changed?
        
    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        version = state[0]
        if version == 3:
            version, internalstate, self.gauss_next = state
            super(Random, self).setstate(internalstate)
        elif version == 2:
            version, internalstate, self.gauss_next = state
            # In version 2, the state was saved as signed ints, which causes
            #   inconsistencies between 32/64-bit systems. The state is
            #   really unsigned 32-bit ints, so we convert negative ints from
            #   version 2 to positive longs for version 3.
            try:
                internalstate = tuple( long(x) % (2**32) for x in internalstate )
            except ValueError, e:
                raise TypeError, e
            super(Random, self).setstate(internalstate)
        else:
            raise ValueError("state with version %s passed to "
                             "Random.setstate() of version %s" %
                             (version, self.VERSION))

    def jumpahead(self, n):
        """Change the internal state to one that is n steps ahead of the
        current state.
        """
        # The super.jumpahead() method uses shuffling to change state,
        # so it needs a large and "interesting" n to work with.  Here,
        # we use hashing to create a large n for the shuffle.
        s = repr(self.getstate()) + repr(n)
        self.setstate(state=s) # might need to use super(Random, self).setstate instead
        
        
        
################################################################################
############################## some sample code ################################
################################################################################

# pseudo-random number generator

seed = 12345678901234567890
count = 0
hash_input = (str(seed) + "," + str(count)).encode('utf-8')
# Apply SHA-256, interpreting hex output as hexadecimal integer
# to yield 256-bit integer (a python "long integer")
hash_output = int(hashlib.sha256(hash_input).hexdigest(),16)

print(hash_output*RECIP_HASHLEN)
count += 1