#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

cd /global/homes/s/siyizhao/projects/fihobi/mock-data-cov/

# config2Abacus=../hod-variation/configs/QSO-fnl30/z4_base.yaml
# srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

# config2Abacus=../hod-variation/configs/QSO-fnl30/z4_base-dv.yaml
# srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

# config2Abacus=../hod-variation/configs/QSO-fnl30/z4_base-dv_test.yaml
# srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

config2Abacus=../hod-variation/configs/QSO-Summit/z4_base-dv.yaml
srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

# python test-z4/plot_ps.py
