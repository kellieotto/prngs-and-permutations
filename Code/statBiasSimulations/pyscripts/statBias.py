from pandas import read_csv
from simulation_utils import *
import math

def findFreqItems(itemCounts, m):
    '''
    Return indices of the m most frequently occurring items
    '''
    ordered = sorted(enumerate(list(itemCounts.values())), key = lambda x: x[1], reverse = True)
    topM = ordered[:m]
    grabIndex = [i[0] for i in topM]
    return grabIndex
    

def findLeastFreqItems(itemCounts, m):
    '''
    Return indices of the m least frequently occurring items
    '''
    ordered = sorted(enumerate(list(itemCounts.values())), key = lambda x: x[1], reverse = False)
    topM = ordered[:m]
    grabIndex = [i[0] for i in topM]
    return grabIndex
  
  
def makePopulation(n, p):
    '''
    Create a population of 0s and 1s
    n = pop size
    p = number of 1s in the population
    '''
    x = [0]*n
    x[:p] = [1]*p
    return(x)


def makeAdversarialPopulation(n, indices, indices2=None):
    '''
    Create a population of 0s, 1s, and -1s
    n = pop size
    indices = locations to put the 1s
    indices = locations to put the -1s (or None if you just one 0/1)
    '''
    x = [0]*n
    for i in indices:
        x[i] = 1
    if indices2 is None:
        return x
    else:
        for i in indices2:
            x[i] = -1
        return x

def getSampleVar(x, uniqueSamples):
    m = 0
    totCnt = 0
    for sam, cnt in uniqueSamples.items():
        m += np.var([x[i] for i in sam], ddof=1)*cnt
        totCnt += cnt
    sampleVar = m/totCnt
    return(sampleVar)
    

def getSampleRange(x, uniqueSamples):
    m = 0
    totCnt = 0
    for sam, cnt in uniqueSamples.items():
        m += np.ptp([x[i] for i in sam])*cnt
        totCnt += cnt
    sampleRange = m/totCnt
    return(sampleRange)
    
    
PRNGs = ['RANDU', 'SD', 'MT', 'SHA256', 'MT_choice']
prng = []
seed = []
nvalues = []
kvalues = []
selected = []

truePopRangeEV = (2*1 + 2*28 + 0*14*27)/435
secondMomentRange = (0 + 1*2*28 + 4*1)/435
truePopRangeSE = math.sqrt(secondMomentRange - truePopRangeEV**2)
popRange = []
aveSampleRange = []
rangeBias = []
rangeSE = [] # SE of the sample range over the reps
rangeRelBias = []

truePopVarEV = (0 + 0.5*2*28 + 2*1)/435
secondMomentVar = (0 + 0.25*2*28 + 4*1)/435
truePopVarSE = math.sqrt(secondMomentVar - truePopVarEV**2)
popVar = []
aveSampleVar = []
varBias = []
varSE = [] # SE of the sample var over the reps
varRelBias = []

for prngname in PRNGs:
    firstorder = read_csv('../rawdata/FO_' + prngname + '.csv', header = None)
    firstorder.columns = ['Item', 'Frequency', 'n', 'k', 'seed']
    
    uniquesamp = read_csv('../rawdata/US_' + prngname + '.csv', header = None)
    uniquesamp.columns = ['Sample', 'Frequency', 'n', 'k', 'seed']
    
    for nn in firstorder.n.unique():
        for kk in firstorder.k.unique():
            for ss in firstorder.seed.unique():

                    					
                # Prep the data
                tmp = firstorder[(firstorder.n == nn) & (firstorder.k == kk) & (firstorder.seed == ss)]
                itemCounts = tmp[['Item','Frequency']].set_index('Item').T.to_dict('list')
            	
                tmp = uniquesamp[(uniquesamp.n == nn) & (uniquesamp.k == kk) & (uniquesamp.seed == ss)]
                reps = sum(tmp.Frequency)
                uniqueSampleCountsbad = tmp[['Sample','Frequency']].set_index('Sample').T.to_dict('records')
                uniqueSampleCounts = dict()
                for k, v in uniqueSampleCountsbad[0].items():
                    k = eval(k)
                    uniqueSampleCounts[k] = v

                
                for meth in ['extreme items', 'least freq sample']:
                    nvalues = nvalues + [nn]
                    kvalues = kvalues + [kk]
                    seed = seed + [ss]
                    prng = prng + [prngname]
                
                    # Bias of range and sample SD: 0s, 1, and -1
                    selected = selected + [meth]
                    if meth == 'extreme items':
                        most_freq = [max(itemCounts, key=itemCounts.get)]
                        least_freq = [min(itemCounts, key=itemCounts.get)]
                        x = makeAdversarialPopulation(nn, most_freq, least_freq)
                    else:
                        least_freq_sample = min(uniqueSampleCounts, key=uniqueSampleCounts.get)
                        x = makeAdversarialPopulation(nn, [ss for ss in least_freq_sample])
                    popRange = popRange + [truePopRangeEV]
                    aveSampleRange = aveSampleRange + [getSampleRange(x, uniqueSampleCounts)]
                    rangeBias = rangeBias + [aveSampleRange[-1] - truePopRangeEV]
                    rangeSE = rangeSE + [truePopRangeSE/math.sqrt(reps)]
                    rangeRelBias = rangeRelBias + [rangeBias[-1]/rangeSE[-1]]
                
                    popVar = popVar + [truePopVarEV]
                    aveSampleVar = aveSampleVar + [getSampleVar(x, uniqueSampleCounts)]
                    varBias = varBias + [aveSampleVar[-1] - truePopVarEV]
                    varSE = varSE + [truePopVarSE/math.sqrt(reps)]
                    varRelBias = varRelBias + [varBias[-1]/varSE[-1]]
                        
                        
d = {'Sample size' : kvalues,
     'Pop size' : nvalues,
     'PRNG' : prng,
     'seed' : seed,
     'method' : selected,
     'Pop Range' : popRange,
     'Avg Sample Range' : aveSampleRange,
     'Range Bias' : rangeBias,
     'Range SE' : rangeSE,
     'Range Bias/SE' : rangeRelBias,
     'Pop Var' : popVar,
     'Avg Sample Var' : aveSampleVar,
     'Var Bias' : varBias,
     'Var SE' : varSE,
     'Var Bias/SE' : varRelBias,
    }
resTable = pd.DataFrame(d)
resTable.to_csv("../results/statBias.csv")