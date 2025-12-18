#!/bin/bash


export THIS_REPO=$HOME/projects/fihobi/
cd ${THIS_REPO}

### Define the Sample, prepare the clustering, and HOD fitting.
tracer="QSO"
zmin=2.8
zmax=3.5
WORK_DIR=${THIS_REPO}/HIP/test/${tracer}_${zmin}_${zmax}
# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pycorr
# python HIP/hip_an_OBSample.py

### Analyze the HOD chain and make mocks.
# source /global/common/software/desi/desi_environment.sh # for the numba version compatibility for AbacusHOD
# python HIP/hip_an_HODchain.py > HIP/hip_an_HODchain.log 2>&1 # would take ~10 mins

### power spectrum of the sampled HOD mocks and p-inference
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pypower
srun -n 1 -c 64 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python HIP/hip_anOBS_mocks.py --tracer ${tracer} --zmin ${zmin} --zmax ${zmax} --work_dir ${WORK_DIR} > ${WORK_DIR}/logs/hip_anOBS_mocks_chain1.log 2>&1 
# if inference='bestfit', 20s for each mock, parallelized over 100 mocks = 100 threads ~ 20s
# if inference='chain', 8 mins for each mock