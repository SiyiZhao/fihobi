#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib

cd /global/homes/s/siyizhao/projects/fihobi/hod-variation

# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi -n 2 -c 64 python scripts/post.py --config configs/QSO-Summit/z0_base.yaml > logs/post_z0_base.log 2>&1

srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi -n 1 -c 64 python scripts/post.py --config configs/QSO-Summit/z4_base.yaml > logs/post_QSO-Summit_z4_base.log 2>&1