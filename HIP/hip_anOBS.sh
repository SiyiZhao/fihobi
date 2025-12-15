#!/bin/bash


export THIS_REPO=$HOME/projects/fihobi/
cd ${THIS_REPO}

### Define the Sample, prepare the clustering, and HOD fitting.
# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pycorr
# python HIP/hip_an_OBSample.py

### Analyze the HOD chain and make mocks.
source /global/common/software/desi/desi_environment.sh # for the numba version compatibility for AbacusHOD
python HIP/hip_an_HODchain.py > HIP/hip_an_HODchain.log 2>&1

### power spectrum of the sampled HOD mocks and p-inference
# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pypower
# python HIP/hip_anOBS_mocks.py
