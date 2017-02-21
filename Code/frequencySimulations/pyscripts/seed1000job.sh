#!/bin/bash
# Job name:
#SBATCH --job-name=test
#
# Number of nodes:
#SBATCH --nodes=1
#
# Processors per node:
#SBATCH --ntasks-per-node=8
## Command(s) to run:
ipcluster start -n $SLURM_NTASKS_PER_NODE &
sleep 50
ipython MT_1000seeds_PIKK_n13_k3.ipy > MT_1000seeds_PIKK_n13_k3.pyout
ipcluster stop