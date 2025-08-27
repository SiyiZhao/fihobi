#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

# srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python ./plot_chain.py --path2config config/chain_y3xi0.yaml > output/y3xi0.txt 2>&1
# srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python ./plot_chain.py --path2config config/chain_y3xi02.yaml > output/y3xi02.txt 2>&1

srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python ./plot_chain_pmn.py --path2config config/lrg_z0_test.yaml > output/y3wpxi02_pmn.txt 2>&1
srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python ./plot_chain_pmn.py --path2config config/lrg_z0_test_fnl30.yaml > output/y3wpxi02_fnl30_pmn.txt 2>&1

exit
