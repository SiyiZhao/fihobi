#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script for running pymultinest sampling to fit multipoles on HOD mock catalogs.

Refer: https://github.com/ahnyu/hod-variation/scripts/run_pocomc.py

Usage
-----
$ python ./run_pmn.py --help
"""

import numpy as np
import argparse
import yaml
import os, sys
# Add the source directory to the PYTHONPATH.
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(current_dir, "..", "source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)

from data_object import data_object
from mypmn import my_pmn
from pmn_helpers import set_global_objects, generate_prior, log_likelihood
from abacusnbody.hod.abacus_hod import AbacusHOD
# from abacusnbody.hod.utils import setup_logging
# setup_logging()

def main():    
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument('--config', type=str, required=True, help="Path to YAML configuration file")
    args = parser.parse_args()

    # Load YAML configuration.
    with open(args.config, 'r') as f:
        config_full = yaml.safe_load(f)    
    # Extract configuration sub-dictionaries.
    sim_params = config_full.get("sim_params", {})
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    fit_params = config_full.get("fit_params", {})
    chain_params = config_full.get("chain_params",{})
    nthread = config_full.get("nthread", 64)
    
    print('config loaded')

    # Initialize the observed data object.
    data_obj = data_object(data_params, HOD_params, clustering_params)
    print('data loaded') 
    
    # Generate the combined prior and parameter mapping.
    prior, param_mapping, prior_types = generate_prior(fit_params)

    # Define active tracers as the keys in fit_params.
    active_tracers = list(fit_params.keys())

    # Build a configuration dictionary for the log-likelihood function.
    global_config = {
        "sim_params": sim_params,
        "HOD_params": HOD_params,
        "clustering_params": clustering_params,
        "param_mapping": param_mapping,
        "fit_params": fit_params,
        "tracers": active_tracers,
        "prior_types": prior_types
    }
    print(global_config)
    
    # create a new abacushod object and load the subsamples
    newBall = AbacusHOD(sim_params, HOD_params, clustering_params)

    # Note: We do NOT set the heavy AbacusHOD object here.
    set_global_objects(data_obj, global_config, nthread, newBall)

    


    # pmn parameters
    chain_prefix = chain_params['chain_prefix']
    output_dir = chain_params['output_dir']
    nlive = chain_params['nlive']
    tol  = chain_params['tol']
    labels = chain_params.get('labels', None)
    # labels = [r"\log M_{\text{cut}}", r"\log M_1", r"\sigma", r"\alpha", r"\kappa", r"\alpha_{\text{c}}", r"\alpha_{\text{s}}"]


    ## define the multinest class
    fit_ = my_pmn(prior, log_likelihood, output_dir, filename=chain_prefix, param_label=labels, live_points=nlive, tol=tol)

    ## prepare the output directory 
    fit_.write_prior_file()

    ## test
    # test = log_likelihood(np.array([11.7209282, 11.1767657, 0.04491125, 0.90375827, 3.85540798, 1.81135532, 1.90593657]))  # example call
    # print('lnL of this MAP:', test)
    # test2 = log_likelihood(np.array([12.07452977, 12.9662911, 0.13082451, 1.32434491, 0.53177675, 1.80176316, 2.7631462 ]))
    # print('lnL of the MAP on fNL=30:', test2)
    ## run 
    fit_.run_pmn()

    ## plot
    # fit_.plot_result(plot_path=pmn_config_params['plot'])

    print('Finished fitting! Take a break!')
  
class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass
    
if __name__ == '__main__':
    main()