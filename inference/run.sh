#!/bin/bash

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

outdir=out
mkdir -p $outdir

# srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python standard.py > $outdir/standard_stdout.log 2> $outdir/standard_stderr.log

# srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python test_fit_p.py > $outdir/test_fit_p_stdout.log 2> $outdir/test_fit_p_stderr.log

srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python fit_p_LRG_z0p5.py > $outdir/fit_p_LRG_z0p5_stdout.log 2> $outdir/fit_p_LRG_z0p5_stderr.log
