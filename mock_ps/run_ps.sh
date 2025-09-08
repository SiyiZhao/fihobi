#!/bin/bash

module load python
source /global/cfs/cdirs/desi/software/desi_environment.sh main
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main


# cat_path=/pscratch/sd/s/siyizhao/fihobi/HODfit_test_z0_fnl30/Abacus_pngbase_c300_ph000/z0.500/galaxies_rsd/LRGs.dat
redshift=0.5

# out_path=output/power_inter3_corrected.npy
# plot_path=output/pole_inter3_corrected.png
# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python ps.py $cat_path --redshift $redshift --output $out_path --plot $plot_path

# out_path=output/power_forEZmocks.npy
# plot_path=output/pole_forEZmocks.png
# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python ps.py $cat_path --redshift $redshift --kmin 0.0015 --kmax 0.2 --nkbins 44 --output $out_path --plot $plot_path

# out_path=output/power_kbin.npy
# plot_path=output/pole_kbin.png
# srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python ps.py $cat_path --redshift $redshift --kmin 0.003 --kmax 0.08 --nkbins 77 --output $out_path --plot $plot_path

cat_path=/pscratch/sd/s/siyizhao/fihobi/EZmocks/EZmock_B2000G280Z0.5N6662830_b0.57d1.3r0c1.09_seed545_RSD.dat
out_path=output/power_seed5.npy
srun -N 1 -C cpu -t 04:00:00 --qos interactive --account desi python ps.py $cat_path --skiprows 0 --redshift $redshift --kmin 0.0015 --kmax 0.2 --nkbins 44 --output $out_path