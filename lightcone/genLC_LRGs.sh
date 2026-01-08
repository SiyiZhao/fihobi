#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/lightcone
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for mockfactory

output=works/lcmock_LRGs_fnl100_base-A
mkdir -p $output

### NGC 
GC='N'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/LRG_NGC_nz_v2.txt'

##### z0.4-0.6
zmin=0.4
zmax=0.6
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/LRG/z0p500/abacus_HF_LRG_0p500_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z0.6-0.8
zmin=0.6
zmax=0.8
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/LRG/z0p725/abacus_HF_LRG_0p725_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z0.8-1.1
zmin=0.8
zmax=1.1
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/LRG/z0p950/abacus_HF_LRG_0p950_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1
