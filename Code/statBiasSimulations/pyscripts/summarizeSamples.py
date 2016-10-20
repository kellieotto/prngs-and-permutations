from pandas import read_csv
from simulation_utils import *

PRNGs = ['RANDU', 'SD', 'MT', 'SHA256', 'MT_choice']
maxProb = []
minProb = []
meanProb = []
maxProbRatio = []
nvalues = []
kvalues = []
prng = []
seed = []

# FO = first order selection probabilities
chisqStatistic_FO = []
chisqDF_FO = []
chisqPvalue_FO = []
rangeStat_FO = []
rangePvalue_FO = []

# US = unique sample selection probabilities
chisqStatistic_US = []
chisqDF_US = []
chisqPvalue_US = []
rangeStat_US = []
rangePvalue_US = []


for prngname in PRNGs:
    firstorder = read_csv('../rawdata/FO_' + prngname + '.csv', header = None)
    firstorder.columns = ['Item', 'Frequency', 'n', 'k', 'seed']
    
    uniquesamp = read_csv('../rawdata/US_' + prngname + '.csv', header = None)
    uniquesamp.columns = ['Sample', 'Frequency', 'n', 'k', 'seed']
    
    for nn in firstorder.n.unique():
        for kk in firstorder.k.unique():
            for ss in firstorder.seed.unique():
                tmp = firstorder[(firstorder.n == nn) & (firstorder.k == kk) & (firstorder.seed == ss)]
                itemCounts = tmp[['Item','Frequency']].set_index('Item').T.to_dict('list')
                
                tmp = uniquesamp[(uniquesamp.n == nn) & (uniquesamp.k == kk) & (uniquesamp.seed == ss)]
                reps = sum(tmp.Frequency)
                uniqueSampleCounts = tmp[['Sample','Frequency']].set_index('Sample').T.to_dict('list')
                
                # First order
                chisqTestResults = conductChiSquareTest(itemCounts)
                chisqDF_FO = chisqDF_FO + [len(itemCounts)-1]
                chisqStatistic_FO = chisqStatistic_FO + [chisqTestResults[0]]
                chisqPvalue_FO = chisqPvalue_FO + [chisqTestResults[1]]
        
                rangeStatObserved = np.ptp(list(itemCounts.values()))
                rangeStat_FO = rangeStat_FO + [rangeStatObserved]
                rangePvalue_FO = rangePvalue_FO + [1-distrMultinomialRange(rangeStatObserved, reps*kk, nn)]
        
                # Unique samples
                chisqTestResults = conductChiSquareTest(uniqueSampleCounts)
                chisqDF_US = chisqDF_US + [len(uniqueSampleCounts)-1]
                chisqStatistic_US = chisqStatistic_US + [chisqTestResults[0]]
                chisqPvalue_US = chisqPvalue_US + [chisqTestResults[1]]
        
                rangeStatObserved = np.ptp(list(uniqueSampleCounts.values()))
                rangeStat_US = rangeStat_US + [rangeStatObserved]
                rangePvalue_US = rangePvalue_US + [1-distrMultinomialRange(rangeStatObserved, reps, comb(nn, kk))]
        
                # Selection probability summary stats
                itemFreq = printItemFreq(itemCounts, reps)
                maxProb = maxProb + [np.amax(list(itemFreq.values()))]
                minProb = minProb + [np.amin(list(itemFreq.values()))]
                meanProb = meanProb + [np.mean(list(itemFreq.values()))]
                maxProbRatio = maxProbRatio + [printMaxProbRatio(itemFreq)]
                nvalues = nvalues + [nn]
                kvalues = kvalues + [kk]
                prng = prng + [prngname]
                seed = seed + [ss]
                
d = {'Sample size' : kvalues,
     'Pop size' : nvalues,
     'PRNG' : prng,
     'Min Prob' : minProb,
     'Mean Prob' : meanProb,
     'Max Prob' : maxProb,
     'Max Selection Prob Ratio' : maxProbRatio,
     'seed' : seed,
     'Chi-squared' : chisqStatistic_FO,
     'Df' : chisqDF_FO,
     'P-value' : chisqPvalue_FO,
     'Range' : rangeStat_FO,
     'Range P-value' : rangePvalue_FO
    }
resTable = pd.DataFrame(d)
resTable.to_csv("../results/firstOrderSummary.csv")


d2 = {'Sample size' : kvalues,
     'Pop size' : nvalues,
     'Number of samples' : comb(np.array(nvalues), np.array(kvalues)),
     'PRNG' : prng,
     'seed' : seed,
     'Chi-squared' : chisqStatistic_US,
     'Df' : chisqDF_US,
     'P-value' : chisqPvalue_US,
     'Range' : rangeStat_US,
     'Range P-value' : rangePvalue_US
    }
resTable2 = pd.DataFrame(d2)
resTable2.to_csv("../results/uniqueSampleSummary.csv")
