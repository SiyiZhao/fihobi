#!/bin/bash
# Usage: bash mock_ps.sh z1

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

cd /global/homes/s/siyizhao/projects/fihobi/mock-data-cov/

tag=$1
dirEZ=/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-${tag}_c302/
# dirEZ=/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-${tag}_c302_fnl300/

# config2Abacus=../hod-variation/configs/QSO-fnl30/${tag}_base-dv.yaml
# srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus 

config2Abacus=../hod-variation/configs/QSO-fnl100/${tag}_base.yaml
srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

config2Abacus=../hod-variation/configs/QSO-fnl100/${tag}_base-dv.yaml
srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

# config2Abacus=../hod-variation/configs/QSO-fnl100/${tag}_base-A-dv.yaml
# srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

# config2Abacus=../hod-variation/configs/QSO-fnl100/${tag}_base-B-dv.yaml
# srun -N 1 -C gpu -t 04:00:00 --qos interactive --account desi_g python scripts/abacus_pkl.py $config2Abacus

mkdir -p out
python scripts/plot_ps.py --tag $tag --dirEZmocks $dirEZ --base c302_v2
