#!/bin/bash
# 
# Usage: 

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

cd /global/homes/s/siyizhao/projects/fihobi/mock-data-cov

srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/pkEZmocks.py
