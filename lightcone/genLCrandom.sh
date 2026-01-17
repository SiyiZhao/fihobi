#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/lightcone


## LRG z0.4-1.1
output=works/lcmock_LRGs_fnl100_base-A/RANDOM
mkdir -p $output
zmin=0.4
zmax=1.1

### NGC 
GC='N'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/LRG_NGC_nz_v2.txt'
cat=${output}/Random_N2.3e9_L6000.dat 
python prep_cutsky.py --catalog_path $cat --boxsize 6000 --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/random_${GC}_${zmin}_${zmax}.log 2>&1

### SGC 
GC='S'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/LRG_SGC_nz_v2.txt'
cat=${output}/Random_N1.5e9_L6000.dat 
python prep_cutsky.py --catalog_path $cat --boxsize 6000 --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/random_${GC}_${zmin}_${zmax}.log 2>&1


### QSO z0.8-3.5
output=works/lcmock_QSOs_fnl100_base-A/RANDOM
mkdir -p $output
zmin=0.8
zmax=3.5

### NGC 
GC='N'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_NGC_nz_v2.txt'
cat=${output}/Random_N3.1e8_L6000.dat 
python prep_cutsky.py --catalog_path $cat --boxsize 6000 --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/random_${GC}_${zmin}_${zmax}.log 2>&1

### SGC 
GC='S'
nz='/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_SGC_nz_v2.txt'
cat=${output}/Random_N2.4e8_L6000.dat 
python prep_cutsky.py --catalog_path $cat --boxsize 6000 --workdir $output --galactic_cap $GC --nz_path $nz --zmin $zmin --zmax $zmax
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c $output/cutsky_${GC}_${zmin}_${zmax}.conf > $output/random_${GC}_${zmin}_${zmax}.log 2>&1
