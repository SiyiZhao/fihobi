#!/bin/bash

#SBATCH --job-name=QSO-Summit_z0_base
#SBATCH --output=/global/homes/s/siyizhao/projects/fihobi/hod-variation/logs/%x_%j.log
#SBATCH --error=/global/homes/s/siyizhao/projects/fihobi/hod-variation/logs/%x_%j.err
#SBATCH --qos=regular
#SBATCH --account=desi
#SBATCH --time=12:00:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=128
#SBATCH -C cpu

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/MultiNest/lib

cd /global/homes/s/siyizhao/projects/fihobi/hod-variation

# srun -n 4 -c 64 python -m abacusnbody.hod.prepare_sim_profiles --path2config configs/QSO-Summit/z0_base.yaml > logs/prepare_sim_profiles.log 2>&1; exit
srun -n 4 -c 128 python scripts/run_pmn.py --config configs/QSO-Summit/z0_base.yaml
