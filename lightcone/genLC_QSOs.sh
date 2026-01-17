#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/lightcone
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for mockfactory

output=works/lcmock_QSOs_fnl100_base-A
mkdir -p $output

### SGC 
GC='S'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_SGC_nz_v2.txt'

##### z0.8-1.1
zmin=0.8
zmax=1.1
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z0p950/abacus_HF_QSO_0p950_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --rewrite_cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z1.1-1.4
zmin=1.1
zmax=1.4
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z1p250/abacus_HF_QSO_1p250_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --rewrite_cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z1.4-1.7
zmin=1.4
zmax=1.7
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z1p550/abacus_HF_QSO_1p550_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --rewrite_cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z1.7-2.3
zmin=1.7
zmax=2.3
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z2p000/abacus_HF_QSO_2p000_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --rewrite_cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z2.3-2.8
zmin=2.3
zmax=2.8
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z2p500/abacus_HF_QSO_2p500_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --rewrite_cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z2.8-3.5
zmin=2.8
zmax=3.5
cat='/pscratch/sd/s/siyizhao/desi-dr2-hod/loa-v2_HODv3/mocks_base-A/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/abacus_HF_QSO_3p000_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
python prep_cutsky.py --catalog_path $cat --rewrite_cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

### NGC 
GC='N'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_NGC_nz_v2.txt'

##### z0.8-1.1
zmin=0.8
zmax=1.1
cat=${output}/box_S_0.8_1.1.dat
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z1.1-1.4
zmin=1.1
zmax=1.4
cat=${output}/box_S_1.1_1.4.dat
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z1.4-1.7
zmin=1.4
zmax=1.7
cat=${output}/box_S_1.4_1.7.dat
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1 

##### z1.7-2.3
zmin=1.7
zmax=2.3
cat=${output}/box_S_1.7_2.3.dat
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z2.3-2.8
zmin=2.3
zmax=2.8
cat=${output}/box_S_2.3_2.8.dat
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1

##### z2.8-3.5
zmin=2.8
zmax=3.5
cat=${output}/box_S_2.8_3.5.dat
python prep_cutsky.py --catalog_path $cat --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/cutsky_${GC}_${zmin}_${zmax}.log 2>&1
