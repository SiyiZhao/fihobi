#!/usr/bin/env python
# coding: utf-8

"""
This is a script for preparing the configuration & slurm files used in HOD fitting.

Usage
-----
$ source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
$ python prep_configs.py

Author: Siyi Zhao
Refer to: https://github.com/ahnyu/hod-variation/blob/main/prep_configs.ipynb
"""

import argparse
import os, sys
file_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(file_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from config_helpers import generate_config, fit_params_overrides, merge_overrides, generate_slurm_launcher
src_dir = os.path.join(file_dir,"..","src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from io_def import load_config, prefix_HOD

### settings -------------------------------------------------------------------
_DEFAULT_FNL = 30
_DEFAULT_HOD = {
    "prefix": 'base',
    "want_dv": False,
    "Assembly": True,
    "BiasENV": False,
    "version": 'v2'
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--config", type=str, default=None, help="Configuration YAML file")
args = parser.parse_args()
if args.config is not None:
    print(f"Loading configuration from {args.config}...")
    configs = load_config(args.config)
else:
    print("No configuration file provided. Using default settings...")
    configs = {}
fnl = configs.get("fnl", _DEFAULT_FNL)
HOD = configs.get("HOD", _DEFAULT_HOD)
match int(fnl):
    case 0:
        sim_model = "Summit"
        sim_name = "AbacusSummit_base_c000_ph000"
    case 30:
        sim_model = "fnl30"
        sim_name = "Abacus_pngbase_c300_ph000"
    case 100:
        sim_model = "fnl100"
        sim_name = "Abacus_pngbase_c302_ph000"
    case _:
        raise ValueError(f"Unsupported fnl value: {fnl}. Expected 0, 30, or 100.")

hod_model = prefix_HOD(HOD)
Assembly = HOD.get("Assembly", False)
BiasENV = HOD.get("BiasENV", False)
want_dv = HOD.get("want_dv", False)

version = HOD.get("version", "v2_logpr")
chain_prefix = f'chain_{version}_' # p6s11, larger prior
clusdir=HOD.get("data_dir", "/global/homes/s/siyizhao/projects/fihobi/data/for_hod/v2_rp6s11/")
fitdir=HOD.get("fit_dir", "/pscratch/sd/s/siyizhao/desi-dr2-hod/")

### Info: different redshift bins ----------------------------------------------
zbins = {
    'LRG': {'z1': (0.4, 0.6), 'z2': (0.6, 0.8), 'z3': (0.8, 1.1)},
    'QSO': {'z1': (0.8, 1.1), 'z2': (1.1, 1.4), 'z3': (1.4, 1.7), 'z4': (1.7, 2.3), 'z5': (2.3, 2.8), 'z6': (2.8, 3.5)}
}
## from prep_data.py output
nbar_all = {
    'LRG': {'z1': 0.0005241, 'z2': 0.0005247, 'z3': 0.0002834}, 
    'QSO': {'z1': 0.00003052, 'z2': 0.00003542, 'z3': 0.00003572, 'z4': 0.00002725, 'z5': 0.00001408, 'z6': 0.000005181} 
}
z_mock_all = {
    'LRG': {'z1': 0.5, 'z2': 0.725, 'z3': 0.95}, 
    'QSO': {'z1': 0.95, 'z2': 1.25, 'z3': 1.55, 'z4': 2.0, 'z5': 2.5, 'z6': 3.0}
}

### Functions ------------------------------------------------------------------
def params_setting(tracer):
    ''' return parameter settings for a given tracer.'''
    if tracer == 'LRG':
        params_labels = ["\log M_{\\text{cut}}","\log M_1","\log \sigma","\\alpha","\kappa", "\\alpha_{\\text{c}}","\\alpha_{\\text{s}}"]
        params_dict = {"names": ["logM_cut","logM1","sigma","alpha","kappa", "alpha_c","alpha_s"], 
                            "lo": [11, 10, -4, -1.0, 0.0, 0.0, 0.0], 
                            "hi": [15, 18, 0, 3.0, 6.0, 3.0, 3.0],
                            "type": ["flat", "flat", "log", "flat", "flat", "flat", "flat"],
                            }
        if Assembly:
            params_labels += ["A_{\\text{cent}}", "A_{\\text{sat}}"]
            params_dict["names"] += ["Acent", "Asat"]
            params_dict["lo"] += [-10.0, -15.0]
            params_dict["hi"] += [10.0, 15.0]
            params_dict["type"] += ["flat", "flat"]
        if BiasENV:
            params_labels += ["B_{\\text{cent}}", "B_{\\text{sat}}"]
            params_dict["names"] += ["Bcent", "Bsat"]
            params_dict["lo"] += [-20.0, -25.0]
            params_dict["hi"] += [20.0, 25.0]
            params_dict["type"] += ["flat", "flat"]
    elif tracer == 'QSO':
        params_labels = ["\log M_{\\text{cut}}","\log M_1","\sigma","\\alpha","\kappa", "\\alpha_{\\text{c}}","\log \\alpha_{\\text{s}}"]
        params_dict = {"names": ["logM_cut","logM1","sigma","alpha","kappa", "alpha_c","alpha_s"], 
                            "lo": [11, 10, 0.0001, -1.0, 0.0, 0.0, -4], 
                            "hi": [15, 18, 3.0, 3.0, 10.0, 3.0, 2.0],
                            "type": ["flat", "flat", "flat", "flat", "flat", "flat", "log"],
                            }
        if Assembly:
            params_labels += ["A_{\\text{cent}}", "A_{\\text{sat}}"]
            params_dict["names"] += ["Acent", "Asat"]
            params_dict["lo"] += [-10.0, -15.0]
            params_dict["hi"] += [10.0, 15.0]
            params_dict["type"] += ["flat", "flat"]
        if BiasENV:
            params_labels += ["B_{\\text{cent}}", "B_{\\text{sat}}"]
            params_dict["names"] += ["Bcent", "Bsat"]
            params_dict["lo"] += [-20.0, -25.0]
            params_dict["hi"] += [20.0, 25.0]
            params_dict["type"] += ["flat", "flat"]
    else:
        raise ValueError("tracer must be 'QSO' or 'LRG'.")
    return params_labels, params_dict

def generate_config_files(tracer):
    ''' generate config files for all redshift bins of a given tracer.'''
    t_zbins = zbins[tracer]
    nbar = nbar_all[tracer]
    z_mock = z_mock_all[tracer]
    params_labels, params_dict = params_setting(tracer)
    config_dir = f"configs/{tracer}-{sim_model}/"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    for tag, (zmin, zmax) in t_zbins.items():
        print(f"{tag}: {zmin} - {zmax}")
        config_path = config_dir+f"{tag}_{hod_model}.yaml" #relative config file path
        tweaks = {
            "sim_params.sim_name": sim_name, 
            "sim_params.output_dir": fitdir+f"mocks_{hod_model}_v2/",
            "HOD_params.want_dv": want_dv,
            "clustering_params.bin_params.logmin": -1.0, # change binning
            "clustering_params.bin_params.nbins": 15,
            "chain_params.chain_prefix": f"{chain_prefix}", # change output chain name
            "chain_params.output_dir": fitdir+f"{tracer}-{sim_model}/{tag}_{hod_model}/",
            "chain_params.labels": params_labels,
            f"data_params.tracer_combos.{tracer}_{tracer}.path2cov": clusdir+f"cov_{tracer}_{zmin}_{zmax}_cut.dat", # change data file
            f"data_params.tracer_combos.{tracer}_{tracer}.path2wp": clusdir+f"wp_{tracer}_{zmin}_{zmax}_cut.dat", # change data file
            f"data_params.tracer_combos.{tracer}_{tracer}.path2xi02": clusdir+f"xi02_{tracer}_{zmin}_{zmax}_cut.dat",
            f"data_params.tracer_density_mean.{tracer}": nbar[tag], # change number density, check output of prep_data.py for numbers
            f"data_params.tracer_density_std.{tracer}": 0.1*nbar[tag],
            "sim_params.z_mock": z_mock[tag], # change redshift
        }
        # change redshift error file
        if tracer == 'QSO':
            tweaks["HOD_params.dv_draw_Q"] = f"/global/homes/s/siyizhao/projects/fihobi/data/dv_draws/QSO_z{zmin}-{zmax}_CDF.npz"
        elif tracer == 'LRG':
            tweaks["HOD_params.dv_draw_L"] = f"/global/homes/s/siyizhao/projects/fihobi/data/dv_draws/LRG_z{zmin}-{zmax}_CDF.npz"
        ## priors specification
        fitspec = {tracer: params_dict,}
        fit_over = fit_params_overrides(fitspec)
        ## generate config
        overrides = merge_overrides(fit_over, tweaks) # combine fit_params and other tweaks
        if tracer=='QSO':
            template='configs/template_QSO_zall.yaml'
        elif tracer=='LRG':
            template='configs/template_LRG_z0.yaml'
        yml = generate_config(template_path=template,
                            overrides=overrides,
                            output_path=config_path)
        print(f'config generated in {config_path}.\n')



def generate_slurm_files(tracer):
    ''' generate slurm files for all redshift bins of a given tracer.
    default version: v2
    '''
    t_zbins = zbins[tracer]
    for tag, (zmin, zmax) in t_zbins.items():
        print(f"{tag}: {zmin} - {zmax}")
        chain_path = fitdir+f"{tracer}-{sim_model}/{tag}_{hod_model}/"
        config_path = f"configs/{tracer}-{sim_model}/{tag}_{hod_model}.yaml" #relative config file path
        launcher_path = f"launchers/{tracer}-{sim_model}_{tag}_{hod_model}.sh" #relative launcher file path
        generate_slurm_launcher(time_hms="8:00:00",
                                config_path=config_path, 
                                chain_path=chain_path,
                                job_name=f"{tracer}-{sim_model}_{tag}_{hod_model}",  #job name
                                output_path=launcher_path,
                                version=version)   
        print(f'launcher generated in {launcher_path}.\n')
        
        
### Usage Example --------------------------------------------------------------
if __name__ == "__main__":
    tracer='QSO'
    
    if tracer not in ['QSO', 'LRG']:
        raise ValueError("tracer must be 'QSO' or 'LRG'")
    
    ############## config files ##############
    generate_config_files(tracer)
    ############## slurm files ##############
    generate_slurm_files(tracer)
    
    tracer='LRG'
    generate_config_files(tracer)
    generate_slurm_files(tracer)
   