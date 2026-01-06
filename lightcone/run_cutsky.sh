#!/bin/bash

cd /global/homes/s/siyizhao/projects/fihobi/lightcone

output=/pscratch/sd/s/siyizhao/fihobi/lc_test
mkdir -p $output

filename=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0_fnl30/Abacus_pngbase_c300_ph000/z0.500/galaxies/LRGs.dat
/global/homes/s/siyizhao/lib/cutsky/CUTSKY -i <(sed '1,15d' $filename) -c cutsky.conf > lc_test.log 2>&1
