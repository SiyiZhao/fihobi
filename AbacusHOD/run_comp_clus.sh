#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
outdir=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0
path2config=config/lrg_z0_test_map.yaml

mkdir -p $outdir
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi --cpu_bind=cores python -m abacusnbody.hod.prepare_sim --path2config $path2config

srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python mock.py --path2config $path2config > $outdir/map_mock.log 2> $outdir/map_mock.err

srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python compare_clus.py --path2config $path2config > $outdir/compare_clus.log 2> $outdir/compare_clus.err

exit
