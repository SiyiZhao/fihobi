#!/bin/bash
#SBATCH -A desi
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 20:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 256

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export OMP_NUM_THREADS=256

outdir=/pscratch/sd/s/siyizhao/fihobi/HOD_fit_y3
mkdir -p $outdir

cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

srun --cpu_bind=cores python nest_xipole.py --path2config config/y3_lrg_smu.yaml > $outdir/n_stdout_5.log 2> $outdir/n_stderr_5.log

