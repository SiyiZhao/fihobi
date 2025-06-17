#!/bin/bash
#SBATCH -A desi
#SBATCH -J AbacusHOD_test
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 1:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 256
#SBATCH -o /pscratch/sd/s/siyizhao/fihobi/mocks/log/test_%J.out
#SBATCH -e /pscratch/sd/s/siyizhao/fihobi/mocks/log/test_%J.err

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD

srun --cpu_bind=cores python -m abacusnbody.hod.prepare_sim --path2config config/abacus_hod.yaml 
srun --cpu_bind=cores python mock.py
python compare_wp.py