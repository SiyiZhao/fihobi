#!/bin/bash


export THIS_REPO=$HOME/projects/fihobi/
cd ${THIS_REPO}

### 1. Define the Sample, prepare the clustering, and HOD fitting.
tracer="QSO"
zmin=0.8
zmax=1.1
WORK_DIR=${THIS_REPO}/HIP/test/${tracer}_${zmin}_${zmax}
mkdir -p ${WORK_DIR}/logs

### Copy the pycorr files from A. Rocher's directory if necessary
cp /global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v2/PIP/cosmo_0/rppi/allcounts_QSO_GCcomb_${zmin}_${zmax}_pip_angular_bitwise_log_njack128_nran4_split20.npy /global/cfs/cdirs/desicollab/users/siyizhao/Y3/loa-v1/v2/PIP/rppi/
cp /global/cfs/cdirs/desi/users/arocher/Y3/loa-v1/v2/PIP/cosmo_0/smu/allcounts_QSO_GCcomb_${zmin}_${zmax}_pip_angular_bitwise_log_njack128_nran4_split20.npy /global/cfs/cdirs/desicollab/users/siyizhao/Y3/loa-v1/v2/PIP/smu/

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pycorr
python HIP/hip_an_OBSample.py --tracer ${tracer} --zmin ${zmin} --zmax ${zmax} --work_dir ${WORK_DIR} > ${WORK_DIR}/logs/hip_anOBS_mocks.log 2>&1

### 2. Analyze the HOD chain and make mocks, 
### and the script for p-inference (if chain mode).
source /global/common/software/desi/desi_environment.sh # for the numba version compatibility for AbacusHOD
chain_root="/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl100/z1_base-A/chain_v2.1_"
python HIP/hip_an_HODchain.py --work_dir ${WORK_DIR} --chain_root ${chain_root} > ${WORK_DIR}/logs/hip_an_HODchain.log 2>&1 # would take ~10 mins

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pypower
# python HIP/plot_sample_2PCF.py --WORKDIR ${WORK_DIR}
python HIP/hip_an_OBS_summary.py --work_dir ${WORK_DIR}

echo "All Done. \n"

# ### power spectrum of the sampled HOD mocks and p-inference
# source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for pypower
# python HIP/hip_anOBS_mocks.py --tracer ${tracer} --zmin ${zmin} --zmax ${zmax} --work_dir ${WORK_DIR} > ${WORK_DIR}/logs/hip_anOBS_mocks.log 2>&1 # 20s for each mock, parallelized over 100 mocks = 100 threads ~ 20s
