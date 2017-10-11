#!/bin/bash
# Job name:
#SBATCH --job-name=sha_serial_2100
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
ipython profile create "cluster2100" --parallel
ipcluster start --profile="cluster2100" -n $SLURM_NTASKS_PER_NODE &
sleep 40
ipython sha_serial_2100.py
ipcluster stop --profile="cluster2100"