#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This is a script for post-processing of the HOD fitting with pyMultiNest. 
- plot chain with GetDist.
- generate best-fit mock and compute clustering.

Usage
---
$ python ./post.py --help
'''

import argparse
import numpy as np
from getdist import loadMCSamples, plots
from getdist import plots
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')
from abacusnbody.hod.abacus_hod import AbacusHOD
# from abacusnbody.hod.utils import setup_logging
# setup_logging()
import os, sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from data_object import data_object
from pmn_helpers import generate_prior
from post_helpers import load_config, bestfit_params, assign_hod, compute_all, plot_all, plot_all_compare

def main(config):
    ## load config
    config_full=load_config(config)
    sim_params = config_full.get("sim_params", {})
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    fit_params = config_full.get("fit_params", {})
    chain_params = config_full.get("chain_params",{})
    nthread = config_full.get("nthread", 32)
    data_obj = data_object(data_params, HOD_params, clustering_params)
    tracer = list(fit_params.keys())[0]
    ## sim_outdir
    sim_outdir = sim_params['output_dir']
        
    ## chain 
    chain_dir=chain_params['output_dir']
    chain_prefix=chain_params['chain_prefix']
    path_plot_getdist = chain_dir + chain_prefix + 'getdist.png'
    ## getdist
    gdsamples = loadMCSamples(chain_dir+chain_prefix, settings={'ignore_rows':0.01})
    bf = bestfit_params(gdsamples)
    ## plot
    g = plots.get_subplot_plotter()
    g.triangle_plot(gdsamples, truths=bf, filled=True, title_limit=1)
    plt.savefig(path_plot_getdist, dpi=300, bbox_inches='tight')
    plt.clf()

    ## generate AbacusHOD object
    ball_profiles = AbacusHOD(sim_params, HOD_params, clustering_params)
    _, param_mapping = generate_prior(fit_params)
    assign_hod(ball_profiles, param_mapping, bf)
    mock_bf,clustering_bf=compute_all(ball_profiles, nthread=nthread, out=True, verbose=True)
    plot_all(data_obj,tracer,clustering_bf,out=chain_dir+chain_prefix+'bestfit_'+tracer+'.png', idxwp=np.arange(6,21), idxxi=np.arange(11,21))
    # plot_all(data_obj,tracer,clustering_bf,out=chain_dir+chain_prefix+'bestfit_'+tracer+'.png')
    ## save bestfit clustering
    if ball_profiles.want_rsd:
        rsd_string = '_rsd'
        if ball_profiles.want_dv:
            rsd_string += '_dv'
    else:
        rsd_string = ''
    outdir = (ball_profiles.mock_dir) / ('galaxies' + rsd_string)
    path2cluster = (outdir) / (tracer + 's_clustering.npy')
    np.save(path2cluster, clustering_bf)
    print("Save bestfit clustering to:", path2cluster)

    
    # ## generate mock in real space
    # mock_bf_r,clustering_bf_r=compute_all(ball_profiles, nthread=nthread, want_rsd=False, out=True, verbose=True)
    # if ball_profiles.want_dv==False:
    #     ## generate mock with dv
    #     mock_bf_dv,clustering_bf_dv=compute_all(ball_profiles, nthread=nthread, want_rsd=True, want_dv=True, out=True, verbose=True)
    #     ## plot compare
    #     plot_all_compare(data_obj,tracer,clustering_bf, [clustering_bf_r, clustering_bf_dv], labels=['w/o rsd', 'w dv'], out=chain_dir+'bestfit_'+tracer+'_comp.png')
    # else:
    #     print("Already have dv, skip generating dv mock")
    #     plot_all_compare(data_obj,tracer,clustering_bf, [clustering_bf_r], labels=['w/o rsd'], out=chain_dir+'bestfit_'+tracer+'_comp.png')
    
    
    return None

class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument('--config', type=str, required=True, help="Path to YAML configuration file")
    
    args = vars(parser.parse_args())
    print('args:', args)
    main(**args)
