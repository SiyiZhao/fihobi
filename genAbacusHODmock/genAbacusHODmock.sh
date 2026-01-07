#!/bin/bash
source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/MultiNest/lib
export OMP_NUM_THREADS=64
config='/global/homes/s/siyizhao/projects/fihobi/hod-variation/configs/QSO-fnl100/z6_base-A.yaml'

# python -m abacusnbody.hod.prepare_sim_profiles --path2config $config
# python AbacusHODmock.py --config $config > genAbacusHODmock.log 2>&1
# mv genAbacusHODmock.log $workdir
python AbacusHODmock.py --config $config --rsd 0 > genAbacusHODmock.log 2>&1
