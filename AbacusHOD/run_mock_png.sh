#!/bin/bash

source /global/common/software/desi/desi_environment.sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
cd /global/homes/s/siyizhao/projects/fihobi/AbacusHOD
outdir=/pscratch/sd/s/siyizhao/fihobi/mock_fnl30_qso
mkdir -p $outdir

(
    config=config/mock_fNL30_QSO_z1pt4.yaml
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python -m abacusnbody.hod.prepare_sim --path2config $config
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python mock.py --path2config $config > $outdir/stdout_z1pt4.log 2> $outdir/stderr_z1pt4.log
) &


(
    config=config/mock_fNL30_QSO_z3pt0.yaml
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python -m abacusnbody.hod.prepare_sim --path2config $config
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python mock.py --path2config $config > $outdir/stdout_z3pt0.log 2> $outdir/stderr_z3pt0.log
) &

(
    config=config/mock_fNL30_QSO_z2pt5.yaml
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python -m abacusnbody.hod.prepare_sim --path2config $config
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python mock.py --path2config $config > $outdir/stdout_z2pt5.log 2> $outdir/stderr_z2pt5.log
) &

(
    config=config/mock_fNL30_QSO_z2pt0.yaml
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python -m abacusnbody.hod.prepare_sim --path2config $config
    srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python mock.py --path2config $config > $outdir/stdout_z2pt0.log 2> $outdir/stderr_z2pt0.log
) &

wait
