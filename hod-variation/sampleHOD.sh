#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib

cd /global/homes/s/siyizhao/projects/fihobi/hod-variation

config=configs/QSO-fnl100/z6_base.yaml
srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi -n 1 -c 64 python scripts/sampleHOD.py --config $config 

