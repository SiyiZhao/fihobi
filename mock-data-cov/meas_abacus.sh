#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

cd /global/homes/s/siyizhao/projects/fihobi/mock-data-cov

#### Abacus info
pdir=/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks/Abacus_pngbase_c300_ph000/z2.000/galaxies_rsd
cat_path=$pdir/QSOs.dat

# pdir=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0_fnl30/Abacus_pngbase_c300_ph000/z0.500/galaxies_rsd
# pdir=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0_fnl100/Abacus_pngbase_c302_ph000/z0.500/galaxies_rsd
# cat_path=$pdir/LRGs.dat

out_path=$pdir/ps_n256.npy
out_for_EZmock=$pdir/pk_ref_n256.txt

#### measure power spectrum with pypower
srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python scripts/abacus_pkl.py $cat_path $out_path $out_for_EZmock



# export PYTHONPATH=$HOME/lib/PyBispec:$PYTHONPATH

# python run_bispec.py