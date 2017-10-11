#!/bin/bash
# Job name:
#SBATCH --job-name=sha_serial_1000
#
# Number of nodes:
#SBATCH --nodes=1
#
# Processors per node:
#SBATCH --ntasks-per-node=30
#
# Notifications for job done and fail
#SBATCH --mail-type=END,FAIL
#
# Send-to address
#SBATCH --mail-user=kellieotto@berkeley.edu

## Command(s) to run:
ipython profile create "cluster1000" --parallel
ipcluster start --profile="cluster1000" -n $SLURM_NTASKS_PER_NODE &
sleep 40
ipython sha_serial_1000.py
ipcluster stop --profile="cluster1000"