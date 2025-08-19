#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type=pip_angular_bitwise
version=v1.1/PIP
verspec=loa-v1
corr=rppi
# outdir=/global/homes/s/siyizhao/data/Y3/$verspec
# outdir=/pscratch/sd/s/siyizhao/fihobi/Y3_log/$verspec
outdir=/global/homes/s/siyizhao/projects/fihobi/data
mkdir -p $outdir

# srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g /global/homes/s/siyizhao/projects/fihobi/clustering/xirunpc.py --tracer LRG --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim 0.6 0.8 --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/rppi_stdout.log 2> $outdir/rppi_stderr.log

mkdir -p $outdir/hodfit
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python combine_wp_xi02.py -o $outdir/hodfit/lrg_data_cov_arocher.h5 > $outdir/combforfit_stdout.log 2> $outdir/combforfit_stderr.log

exit
