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

############## settings ##############
# sim_model = "Summit"
# sim_name = "AbacusSummit_base_c000_ph000"
sim_model = "fnl30"
sim_name = "Abacus_pngbase_c300_ph000"

hod_model = "base" 
# hod_model = "base-dv" # with redshift error
# want_dv = False if hod_model=="base" else True
want_dv = True 
# want_dv = False
if want_dv:
    hod_model += "-dv"

chain_prefix = 'chain_'

############## for different redshift bins ##############
qso_bins = {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7), 'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
z_mock = {'z1': 0.95, 'z2': 1.25, 'z3': 1.55, 'z4': 2.0, 'z5': 2.5, 'z6': 3.0}
nbar = {'z1': 0.00003073, 'z2': 0.00003566, 'z3': 0.00003606, 'z4': 0.00001419, 'z5': 0.000007876, 'z6': 0.000005216} # from prep_data.py output
# ! attention: z5 and z6 may have large alpha_s, and z6 has larger logM1, need to increase upper bound 

for tag, (zmin, zmax) in qso_bins.items():
    print(f"{tag}: {zmin} - {zmax}")
    config_path = f"configs/QSO-{sim_model}/{tag}_{hod_model}.yaml" #relative config file path
    tweaks_qso = {
        "sim_params.sim_name": sim_name, 
        "HOD_params.want_dv": want_dv,
        "HOD_params.dv_draw_Q": f"/global/homes/s/siyizhao/projects/fihobi/data/dv_draws/QSO_z{zmin}-{zmax}_CDF.npz", # change redshift error file
        "chain_params.chain_prefix": f"{chain_prefix}", # change output chain name
        "chain_params.output_dir": f"/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-{sim_model}/{tag}_{hod_model}/",
        "data_params.tracer_combos.QSO_QSO.path2cov": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1/cov_QSO_{zmin}_{zmax}_cut.dat", # change data file
        "data_params.tracer_combos.QSO_QSO.path2wp": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1/wp_QSO_{zmin}_{zmax}_cut.dat",
        "data_params.tracer_combos.QSO_QSO.path2xi02": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1/xi02_QSO_{zmin}_{zmax}_cut.dat",
        "data_params.tracer_density_mean.QSO": nbar[tag], # change number density, check output of prep_data.py for numbers
        "data_params.tracer_density_std.QSO": 0.1*nbar[tag],
        "sim_params.z_mock": z_mock[tag], # change redshift
    }

    fitspec_qso = {
        "QSO": {"names": ["logM_cut","logM1","sigma","alpha","kappa", "alpha_c","alpha_s"], 
                "lo": [11, 12.5, 0.001, 0.0, 0.0, 0.0, 0.0], 
                "hi": [14, 17.5, 2.0, 3.0, 5.0, 3.0, 8.0]},
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
    chain_path = f"/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-{sim_model}/{tag}_{hod_model}/"
    config_path = f"configs/QSO-{sim_model}/{tag}_{hod_model}.yaml" #relative config file path
    launcher_path = f"launchers/QSO-{sim_model}_{tag}_{hod_model}.sh" #relative launcher file path
    generate_slurm_launcher(time_hms="6:00:00",
                            config_path=config_path, 
                            chain_path=chain_path,
                            job_name=f"QSO-{sim_model}_{tag}_{hod_model}",  #job name
                            output_path=launcher_path,)   
    print('launcher generated.\n')
