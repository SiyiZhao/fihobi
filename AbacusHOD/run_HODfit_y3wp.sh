#!/bin/bash
#SBATCH -A desi
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 10:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 256

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export OMP_NUM_THREADS=256
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

outdir=/pscratch/sd/s/siyizhao/fihobi/HOD_fit_y3wp
mkdir -p $outdir

cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

srun --cpu_bind=cores python nested.py --path2config config/lrg_y3wp.yaml > $outdir/stdout_.log 2> $outdir/stderr_.log

