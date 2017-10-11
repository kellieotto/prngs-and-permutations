#!/bin/bash
# Job name:
#SBATCH --job-name=sha_serial_200
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
ipython profile create "cluster200" --parallel
ipcluster start --profile="cluster200" -n $SLURM_NTASKS_PER_NODE &
sleep 40
ipython sha_serial_200.py
ipcluster stop --profile="cluster200"