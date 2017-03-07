#!/bin/bash
# Job name:
#SBATCH --job-name=multinomial-sprt
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
sleep 50
ipython multinomial_"${SLURM_ARRAY_TASK_ID}".py > multinomial_"${SLURM_ARRAY_TASK_ID}".pyout
ipcluster stop --profile="cluster-${SLURM_ARRAY_TASK_ID}"