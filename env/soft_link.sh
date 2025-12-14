#!/bin/bash
# assume on NERSC 

source env.sh
cd ${THIS_REPO}/data

ln -s /global/cfs/cdirs/desi/users/siyizhao/Y3 clustering
ln -s /pscratch/sd/s/siyizhao/desi-dr2-hod desi-dr2-hod
ln -s /pscratch/sd/s/siyizhao/AbacusSummit/subsample_desidr2_profile_withAB/ AbacusSubsample