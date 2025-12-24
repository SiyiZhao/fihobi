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

import argparse, sys
import numpy as np
from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
from abacusnbody.hod.abacus_hod import AbacusHOD
# from abacusnbody.hod.utils import setup_logging
# setup_logging()

from pathlib import Path
THIS_REPO = Path(__file__).parent.parent.parent

src_dir = THIS_REPO / 'src'
if src_dir not in sys.path:
    sys.path.insert(0, str(src_dir))
from io_def import load_config, plot_style, path_to_clustering, write_catalogs
from abacus_helper import assign_hod, reset_fic, set_theory_density, compute_mock_and_multipole

source_dir = THIS_REPO / 'hod-variation' / 'source'
if source_dir not in sys.path:
    sys.path.insert(0, str(source_dir))
from data_object import data_object
from chain_helper import bestfit_params
from post_helpers import plot_all

plot_style()

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
    tracers = list(fit_params.keys())
    tracer = tracers[0]
        
    ## chain 
    chain_dir=chain_params['output_dir']
    chain_prefix=chain_params['chain_prefix']
    path_plot_getdist = chain_dir + chain_prefix + 'getdist.png'
    ## getdist
    gdsamples = loadMCSamples(chain_dir+chain_prefix, settings={'ignore_rows':0.01})
    bf = bestfit_params(gdsamples)
    ## plot
    g = plots.get_subplot_plotter()
    g.triangle_plot(gdsamples, markers=bf, marker_args={'ls':'-', 'lw':1.5}, filled=True, title_limit=1)
    plt.savefig(path_plot_getdist, dpi=300, bbox_inches='tight')
    plt.clf()

    ## generate AbacusHOD object
    ball_profiles = AbacusHOD(sim_params, HOD_params, clustering_params)
    assign_hod(ball_profiles, fit_params, bf)
    ngal_dict, fsat_dict = reset_fic(ball_profiles, tracers, data_obj.density_mean, nthread=nthread)
    density_bf = set_theory_density(ngal_dict, ball_profiles.params['Lbox']**3, data_obj.density_mean, tracers, nthread=nthread)
    
    mock_bf,clustering_bf=compute_mock_and_multipole(ball_profiles, nthread=nthread, out=False, verbose=True)
    out_root = sim_params.get('output_dir')

    write_catalogs(ball_profiles, mock_bf, fit_params, out_root=out_root, prefix=f'MAP')
    
    loglike_bf = data_obj.compute_loglike(clustering_bf, density_bf)
    print("Best-fit loglike:", loglike_bf)
    
    plot_all(data_obj,tracer,clustering_bf,out=chain_dir+chain_prefix+'bestfit_'+tracer+'.png', idxwp=np.arange(6,21), idxxi=np.arange(11,21))

    ## save bestfit clustering
    path2cluster  = path_to_clustering(sim_params, tracer=tracer, prefix='MAP')
    np.save(path2cluster, clustering_bf)
    print("Save bestfit clustering to:", path2cluster)

    
    # ## generate mock in real space
    # mock_bf_r,clustering_bf_r=compute_mock_and_multipole(ball_profiles, nthread=nthread, want_rsd=False, out=True, verbose=True)
    # if ball_profiles.want_dv==False:
    #     ## generate mock with dv
    #     mock_bf_dv,clustering_bf_dv=compute_mock_and_multipole(ball_profiles, nthread=nthread, want_rsd=True, want_dv=True, out=True, verbose=True)
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
