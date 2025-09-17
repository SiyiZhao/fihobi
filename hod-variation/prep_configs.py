#!/usr/bin/env python
# coding: utf-8

"""
This is a script for preparing the configuration & slurm files used in HOD fitting.

Refer to: https://github.com/ahnyu/hod-variation/blob/main/prep_configs.ipynb

Usage
-----
$ source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
$ python prep_configs.py
"""

import os, sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from config_helpers import generate_config, fit_params_overrides, merge_overrides, generate_slurm_launcher

## z0: 0.8-2.1  
# yml = generate_config(template_path='configs/template_QSO_zall.yaml',
#                       output_path='configs/QSO-Summit/z0_base.yaml')

############## for different redshift bins ##############
# ! attention: z5 and z6 may have large alpha_s, and z6 has larger logM1, need to increase upper bound 
qso_bins = {'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
z_mock = {'z4': 2.0, 'z5': 2.5, 'z6': 3.0}
nbar = {'z4': 0.00001419, 'z5': 0.000007876, 'z6': 0.000005216} # from prep_data.py output

for tag, (zmin, zmax) in qso_bins.items():
    print(f"{tag}: {zmin} - {zmax}")
    config_path = f"configs/QSO-Summit/{tag}_base-dv.yaml" #relative config file path
    tweaks_qso = {
        "HOD_params.dv_draw_Q": f"/global/cfs/projectdirs/desi/users/jiaxiyu/repeated_observations/EDR_vs_Y3/LSS-scripts_repeats/QSO_z{zmin}-{zmax}_CDF.npz", # change redshift error file
        "chain_params.chain_prefix": f"QSO_{tag}_base", # change output chain name
        "chain_params.output_dir": f"/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO/{tag}/",
        "data_params.tracer_combos.QSO_QSO.path2cov": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1/cov_QSO_{zmin}_{zmax}_cut.dat", # change data file
        "data_params.tracer_combos.QSO_QSO.path2wp": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1/wp_QSO_{zmin}_{zmax}_cut.dat",
        "data_params.tracer_combos.QSO_QSO.path2xi02": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1/xi02_QSO_{zmin}_{zmax}_cut.dat",
        "data_params.tracer_density_mean.LRG": nbar[tag], # change number density, check output of prep_data.py for numbers
        "data_params.tracer_density_std.LRG": 0.1*nbar[tag],
        "sim_params.z_mock": z_mock[tag], # change redshift
    }

    fitspec_qso = {
        "QSO": {"names": ["logM_cut","logM1","sigma","alpha","kappa", "alpha_c","alpha_s"], 
                "lo": [11, 12.5, 0.001, 0.0, 0.0, 0.0, 0.0], 
                "hi": [14, 15.5, 2.0, 3.0, 5.0, 3.0, 5.0]},
    }
    fit_over_qso = fit_params_overrides(fitspec_qso)

    overrides_qso = merge_overrides(fit_over_qso, tweaks_qso) # combine fit_params and other tweaks

    yml = generate_config(template_path='configs/template_QSO_zall.yaml',
                        overrides=overrides_qso,
                        output_path=config_path)
    print('config generated.\n')






## if add assembly bias

# fitspec_lrg_A = {
#     "LRG": {"names": ["logM_cut","logM1","sigma","alpha", "kappa","alpha_c","alpha_s","Acent", "Asat"], # HOD params to vary
#             "lo": [11, 12.5, 0.001, 0.0, 0.0, 0.0, 0.0, -1.0, -1.0],  # lower bound
#             "hi": [14, 15.5, 2.0, 3.0, 5.0, 2.0, 2.0, 1.0, 1.0]}, # upper bound
# }
# fit_over_lrg_A = fit_params_overrides(fitspec_lrg_A)

# tweaks_lrg_z0_A = {
#     "chain_params.chain_prefix": "LRG_z0_base_A", # change output chain name
# }

# overrides_lrg_z0_A = merge_overrides(fit_over_lrg_A, tweaks_lrg_z0_A) # combine fit_params and other tweaks

# yml = generate_config(template_path='configs/LRG/z0_base.yaml',
#                       overrides=overrides_lrg_z0_A,
#                       output_path='configs/LRG/z0_base_A.yaml')



############## slurm files ##############
for tag, (zmin, zmax) in qso_bins.items():
    print(f"{tag}: {zmin} - {zmax}")
    chain_path = f"/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-Summit/{tag}_base-dv/"
    config_path = f"configs/QSO-Summit/{tag}_base-dv.yaml" #relative config file path
    launcher_path = f"launchers/QSO-Summit_{tag}_base-dv.sh" #relative launcher file path
    generate_slurm_launcher(time_hms="12:00:00", #wall time, depending on number of samples you want, usually set to 24 or 48, you can always resume from a .state file if not enough time
                            config_path=config_path, 
                            chain_path=chain_path,
                            job_name=f"QSO-Summit_{tag}_base",  #job name
                            output_path=launcher_path,)   
    print('launcher generated.\n')
