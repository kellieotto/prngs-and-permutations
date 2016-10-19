all: results/*.csv

RAW = $(wildcard rawdata/*.csv)

results/statBias.csv : $(RAW)
	cd pyscripts; python3 statBias.py

results/uniqueSampleSummary.csv results/firstOrderSummary.csv : $(RAW)
	cd pyscripts; python3 summarizeSamples.py

rawdata/FO_%.csv rawdata/US_%.csv: pyscripts/%.py
	rm rawdata/FO_$*.csv rawdata/US_$*.csv; cd $(<D); python3 $(<F)