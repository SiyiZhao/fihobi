#!/bin/bash
# please read before run 

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

# outdir=../data/for_hod/v1.1/
# mkdir -p $ourdir

python prep_data.py > output/arocher_meas.txt

# ! change path & zbin

python prep_data.py > output/hanyu_meas.txt

# then prepare the config files in config/ and slurm scripts in launchers/
python prep_configs.py > output/prep_configs.log 2>&1
