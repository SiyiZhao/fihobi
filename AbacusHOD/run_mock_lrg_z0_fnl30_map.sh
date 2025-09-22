#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$HOME/lib/abacusutils-re:$PYTHONPATH

config=config/lrg_z0_test_fnl30_map.yaml
outdir=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0_fnl30
# mkdir -p $outdir
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python -m abacusnbody.hod.prepare_sim --path2config $config

srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python mock.py --path2config $config > $outdir/mock_stdout.log 2> $outdir/mock_stderr.log

exit
