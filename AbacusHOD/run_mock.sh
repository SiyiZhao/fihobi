#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
outdir=/pscratch/sd/s/siyizhao/fihobi/mocks_yuan24_Tab3_Col4
mkdir -p $outdir
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

# srun --cpu_bind=cores python -m abacusnbody.hod.prepare_sim --path2config config/abacus_hod.yaml 
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python mock.py > $outdir/stdout.log 2> $outdir/stderr.log

srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python compare_wp.py > $outdir/compare_wp.log 2> $outdir/compare_wp.err

exit
