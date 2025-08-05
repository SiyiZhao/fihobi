#!/bin/bash
#SBATCH -A desi
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 48:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 256

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export OMP_NUM_THREADS=256

outdir=/pscratch/sd/s/siyizhao/fihobi/HOD_fit_y3xi02
mkdir -p $outdir

cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

srun --cpu_bind=cores python nest_xipole.py --path2config config/lrg_y3xi02.yaml > $outdir/stdout.log 2> $outdir/stderr.log

