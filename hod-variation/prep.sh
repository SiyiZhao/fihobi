#!/bin/bash
# please read before run 

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
cd /global/homes/s/siyizhao/projects/fihobi/hod-variation

# outdir=../data/for_hod/v2_rp6s11/
# mkdir -p $ourdir

# QSO in v2
python prep_data.py > output/prep_data_QSO_v2.txt

# ! change tracer to highz-QSO and version to v1.1
python prep_data.py > output/prep_data_highz-QSO_v1.1.txt

# ! change tracer to LRG
python prep_data.py > output/prep_data_LRG.txt
# ! change version to v2
python prep_data.py > output/prep_data_LRG_v2.txt

# then prepare the config files in config/ and slurm scripts in launchers/
python prep_configs.py > output/prep_configs.log 2>&1
