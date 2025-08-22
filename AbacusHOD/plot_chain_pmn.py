#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This is a script for plotting results from pyMultiNest runs. 
Using GetDist.

Usage
---
$ python ./plot_chain_pmn.py --help
'''

import argparse
import yaml
import numpy as np
from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')
from plot_hod import plot_HOD_stat


DEFAULTS = {}
DEFAULTS['path2config'] = 'config/lrg_z0_test.yaml'

def main(path2config):
    ## load the yaml parameters
    config = yaml.safe_load(open(path2config))
    pmn_config_params = config['pmn_config_params']
    ### input
    dir = pmn_config_params['path2output']
    prefix = pmn_config_params['chainsPrefix']
    ### output
    path_plot_getdist = pmn_config_params['plot']
    path_hod = pmn_config_params.get('plot_hod', None)

    ## getdist
    gdsamples = loadMCSamples(dir+prefix, settings={'ignore_rows':0.01})   
    samples, weights = gdsamples.samples, gdsamples.weights
    ## max weight
    max_weight_idx = np.argmax(weights)
    max_logwt_sample = samples[max_weight_idx]
    print('MAP:', max_logwt_sample)
    # truths = [12.78,13.94,0.17,1.07,0.55] # yuan's results
    truths = max_logwt_sample

    g = plots.get_subplot_plotter()
    g.triangle_plot(gdsamples, truths=truths, filled=True, title_limit=1)
    plt.savefig(path_plot_getdist, dpi=300, bbox_inches='tight')
    plt.clf()

    ### plot hod
    if path_hod is not None:
        plot_HOD_stat(samples, weights, path=path_hod, logMcut=truths[0])


class ArgParseFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


if __name__ == '__main__':
    # Nthread = os.cpu_count()
    # print("Number of threads set to:", Nthread)

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=ArgParseFormatter
    )
    parser.add_argument(
        '--path2config',
        dest='path2config',
        type=str,
        help='Path to config file.',
        default=DEFAULTS['path2config'],
    )
    
    args = vars(parser.parse_args())
    print('args:', args)
    main(**args)
