all: results/*.csv

RAW = $(wildcard rawdata/*.csv)

results/sampleMeanBias.csv : $(RAW)
	cd pyscripts; python sampleMeanBias.py

results/uniqueSampleSummary.csv results/firstOrderSummary.csv : $(RAW)
	cd pyscripts; python summarizeSamples.py

rawdata/FO_%.csv rawdata/US_%.csv: pyscripts/pythonRandomSamples_%.py
	rm rawdata/FO_$*.csv rawdata/US_$*.csv; cd $(<D); python $(<F)