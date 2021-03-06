#!/bin/bash
# Job name:
#SBATCH --job-name=derange
#
# Number of nodes:
#SBATCH --nodes=1
#
# Processors per node:
#SBATCH --ntasks-per-node=12
#
# Notifications for job done and fail
#SBATCH --mail-type=END,FAIL
#
# Send-to address
#SBATCH --mail-user=kellieotto@berkeley.edu

## Command(s) to run:
ipython profile create "cluster-${SLURM_ARRAY_TASK_ID}" --parallel
ipcluster start --profile="cluster-${SLURM_ARRAY_TASK_ID}" -n $SLURM_NTASKS_PER_NODE &
sleep 45
ipython derangement-scripts/derangements_"${SLURM_ARRAY_TASK_ID}".py
ipcluster stop --profile="cluster-${SLURM_ARRAY_TASK_ID}"