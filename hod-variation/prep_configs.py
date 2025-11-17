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
# sim_model = "fnl30"
# sim_name = "Abacus_pngbase_c300_ph000"
sim_model = "fnl100"
sim_name = "Abacus_pngbase_c302_ph000"

hod_model = "base" 
# Assembly=True
Assembly=False 
BiasENV=True
# BiasENV=False
want_dv = True 
# want_dv = False
if Assembly:
    hod_model += "-A"
if BiasENV:
    hod_model += "-B"
if want_dv:
    hod_model += "-dv"

# chain_prefix = 'chain_'
chain_prefix = 'chain_rp6s11_11M118_'

############## for different redshift bins ##############
qso_bins = {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7), 'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
z_mock = {'z1': 0.95, 'z2': 1.25, 'z3': 1.55, 'z4': 2.0, 'z5': 2.5, 'z6': 3.0}
nbar = {'z1': 0.00003073, 'z2': 0.00003566, 'z3': 0.00003606, 'z4': 0.00001419, 'z5': 0.000007876, 'z6': 0.000005216} # from prep_data.py output

for tag, (zmin, zmax) in qso_bins.items():
    print(f"{tag}: {zmin} - {zmax}")
    config_path = f"configs/QSO-{sim_model}/{tag}_{hod_model}.yaml" #relative config file path
    tweaks_qso = {
        "sim_params.sim_name": sim_name, 
        "sim_params.output_dir": f"/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_{hod_model}/",
        "HOD_params.want_dv": want_dv,
        "HOD_params.dv_draw_Q": f"/global/homes/s/siyizhao/projects/fihobi/data/dv_draws/QSO_z{zmin}-{zmax}_CDF.npz", # change redshift error file
        "clustering_params.bin_params.logmin": -1.0, # change binning
        "clustering_params.bin_params.nbins": 15,
        "chain_params.chain_prefix": f"{chain_prefix}", # change output chain name
        "chain_params.output_dir": f"/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-{sim_model}/{tag}_{hod_model}/",
        "chain_params.labels": ["\log M_{\\text{cut}}","\log M_1","\sigma","\\alpha","\kappa", "\\alpha_{\\text{c}}","\\alpha_{\\text{s}}"],
        "data_params.tracer_combos.QSO_QSO.path2cov": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1_rp6s11/cov_QSO_{zmin}_{zmax}_cut.dat", # change data file
        "data_params.tracer_combos.QSO_QSO.path2wp": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1_rp6s11/wp_QSO_{zmin}_{zmax}_cut.dat",
        "data_params.tracer_combos.QSO_QSO.path2xi02": f"/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v1.1_rp6s11/xi02_QSO_{zmin}_{zmax}_cut.dat",
        "data_params.tracer_density_mean.QSO": nbar[tag], # change number density, check output of prep_data.py for numbers
        "data_params.tracer_density_std.QSO": 0.1*nbar[tag],
        "sim_params.z_mock": z_mock[tag], # change redshift
    }

    fitspec_qso = {
        "QSO": {"names": ["logM_cut","logM1","sigma","alpha","kappa", "alpha_c","alpha_s"], 
                "lo": [11, 11, 0.001, 0.0, 0.0, 0.0, 0.0], 
                "hi": [14, 18, 2.0, 3.0, 5.0, 3.0, 10.0]},
    }
    if Assembly:
        tweaks_qso["chain_params.labels"] += ["A_{\\text{cent}}", "A_{\\text{sat}}"]
        fitspec_qso["QSO"]["names"] += ["Acent", "Asat"]
        fitspec_qso["QSO"]["lo"] += [-5.0, -5.0]
        fitspec_qso["QSO"]["hi"] += [5.0, 5.0]
    if BiasENV:
        tweaks_qso["chain_params.labels"] += ["B_{\\text{cent}}", "B_{\\text{sat}}"]
        fitspec_qso["QSO"]["names"] += ["Bcent", "Bsat"]
        fitspec_qso["QSO"]["lo"] += [-5.0, -5.0]
        fitspec_qso["QSO"]["hi"] += [5.0, 5.0]

    fit_over_qso = fit_params_overrides(fitspec_qso)
    overrides_qso = merge_overrides(fit_over_qso, tweaks_qso) # combine fit_params and other tweaks

    yml = generate_config(template_path='configs/template_QSO_zall.yaml',
                        overrides=overrides_qso,
                        output_path=config_path)
    print('config generated.\n')


############## slurm files ##############
for tag, (zmin, zmax) in qso_bins.items():
    print(f"{tag}: {zmin} - {zmax}")
    chain_path = f"/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-{sim_model}/{tag}_{hod_model}/"
    config_path = f"configs/QSO-{sim_model}/{tag}_{hod_model}.yaml" #relative config file path
    launcher_path = f"launchers/QSO-{sim_model}_{tag}_{hod_model}.sh" #relative launcher file path
    generate_slurm_launcher(time_hms="8:00:00",
                            config_path=config_path, 
                            chain_path=chain_path,
                            job_name=f"QSO-{sim_model}_{tag}_{hod_model}",  #job name
                            output_path=launcher_path,)   
    print('launcher generated.\n')
