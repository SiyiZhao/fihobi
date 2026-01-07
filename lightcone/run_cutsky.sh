#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/lightcone
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for mockfactory

output=works/test_lcmock
mkdir -p $output

GC='N'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_NGC_nz_v2.txt'

zmin=2.8
zmax=3.5
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/abacus_HF_QSO_3p000_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'

python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax

/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1
