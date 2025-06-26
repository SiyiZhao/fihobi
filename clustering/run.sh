#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

export PYTHONPATH=$PYTHONPATH:$HOME/lib/LSS/py

weight_type=pip_angular_bitwise
version=v1.1/PIP
verspec=loa-v1
corr=smu
outdir=/global/homes/s/siyizhao/data/Y3/$verspec
# outdir=/pscratch/sd/s/siyizhao/fihobi/Y3_log/$verspec
mkdir -p $outdir

srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g /global/homes/s/siyizhao/projects/fihobi/clustering/xirunpc.py --tracer LRG --survey DA2 --verspec $verspec --nthreads 256 --version $version --region NGC SGC --corr_type $corr --njack 128 --zlim 0.6 0.8 --weight_type $weight_type --bin_type log --nreal=128 --outdir $outdir > $outdir/xirunpc_stdout.log 2> $outdir/xirunpc_stderr.log

mkdir -p $outdir/hodfit
srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python pcforfit.py --dir $outdir --fix LRG_GCcomb_0.6_0.8_pip_angular_bitwise_log_njack128_nran4_split20 --check > $outdir/pcforfit_stdout.log 2> $outdir/pcforfit_stderr.log

exit
