from pandas import read_csv
from simulation_utils import *
import math

PRNGs = ['RANDU', 'SD', 'MT', 'SHA256']
popMean = []
sampleMean = []
nvalues = []
kvalues = []
prng = []
seed = []
bias = []
relBias = []
theoreticalSE = []
p = [5, 10, 20]


for prngname in PRNGs:
    firstorder = read_csv('../rawdata/FO_' + prngname + '.csv', header = None)
    firstorder.columns = ['Item', 'Frequency', 'n', 'k', 'seed']
    
    uniquesamp = read_csv('../rawdata/US_' + prngname + '.csv', header = None)
    uniquesamp.columns = ['Sample', 'Frequency', 'n', 'k', 'seed']
    
    for nn in firstorder.n.unique():
        for kk in firstorder.k.unique():
            for ss in firstorder.seed.unique():
                for pp in p:
                    if pp >= nn or kk >= nn:
                        continue
					
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
                        
                    # Bias of sample mean: 0s and 1s
	            	most_freq_p = findFreqItems(itemCounts, pp)
                    x = makeAdversarialPopulation(nn, most_freq_p)
                    truePopMean = getPopMean(x)
                    popMean = popMean + [truePopMean]
                    sampleMean = sampleMean + [getSampleMean(x, uniqueSampleCounts)]
                    nvalues = nvalues + [nn]
                    kvalues = kvalues + [kk]
                    prng = prng + [prngname]
                    estimBias = sampleMean[-1] - truePopMean
                    bias = bias + [estimBias]
                    relBias = relBias + [estimBias/truePopMean]
                    seed = seed + [100]
                    theoreticalSE = theoreticalSE + \
                        [math.sqrt(truePopMean*(1-truePopMean)*(nn-kk)/(reps * kk * (nn-1)))]
                        
                        
d = {'Sample size' : kvalues,
     'Pop size' : nvalues,
     'Pop Mean' : popMean,
     'Sample Mean' : sampleMean,
     'Bias' : bias,
     'Relative bias' : relBias,
     'seed' : seed,
     'Theoretical SE' : theoreticalSE,
     'Bias/Theoretical SE' : np.array(bias)/np.array(theoreticalSE)
    }
resTable = pd.DataFrame(d)
resTable.to_csv("../results/sampleMeanBias.csv")