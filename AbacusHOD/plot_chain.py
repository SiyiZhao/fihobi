#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This is a script for plotting results from Dynesty runs. 
Using its plotting tools and GetDist.

Usage
---
$ python ./plot_chain.py --help
'''

import argparse
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')
from plot_hod import plot_HOD_stat

DEFAULTS = {}
DEFAULTS['path2config'] = 'config/chain_y3wp.yaml'

def run_dyplot(path_plot_run, path_plot_trace, path_plot_corner, truths, res):
    from dynesty import plotting as dyplot

    ndim = 5
    labels = [r"$\log M_{\text{cut}}$", r"$\log M_1$", r"$\sigma$", r"$\alpha$", r"$\kappa$"]
    ### plot run
    if path_plot_run is not None:
        lnz_truth = ndim * -np.log(2 * 10.)  # analytic evidence solution
        fig, axes = dyplot.runplot(res, lnz_truth=lnz_truth)  # summary (run) plot
        plt.savefig(path_plot_run, dpi=300, bbox_inches='tight')
        plt.clf()
    ### trace
    if path_plot_trace is not None:
        fig, axes = dyplot.traceplot(res, truths=truths, labels=labels, truth_color='black', show_titles=True, trace_cmap='viridis', connect=True, connect_highlight=range(5))
        plt.savefig(path_plot_trace, dpi=300, bbox_inches='tight')
        plt.clf()
    ### corner plot
    if path_plot_corner is not None:
        fig, ax = dyplot.cornerplot(res, color='blue', truths=truths, labels=labels, truth_color='black', show_titles=True, max_n_ticks=3, quantiles=None)
        plt.savefig(path_plot_corner, dpi=300, bbox_inches='tight')
        plt.clf()



# def read_prior_cut(path2config):
#     prior_cut = {}
#     config = yaml.safe_load(open(path2config))
#     fit_params = config['dynesty_fit_params']
#     for key in fit_params.keys():
#         prior_cut[key] = fit_params[key][2:4]  # [min, max]
#     return prior_cut

def run_getdist(samples, weights, truths, path_plot_getdist):  
    from getdist import MCSamples, plots

    names = ["logM_cut", "logM1", "sigma", "alpha", "kappa"]
    labels = [r"\log M_{\text{cut}}", r"\log M_1", r"\sigma", r"\alpha", r"\kappa"]
    # prior_cut = read_prior_cut(path2config)
    # print(f"Prior cut: {prior_cut}")

    # gdsamples = MCSamples(samples=samples, weights=weights, names=names, labels=labels, ranges=prior_cut)
    gdsamples = MCSamples(samples=samples, weights=weights, names=names, labels=labels)

    g = plots.get_subplot_plotter()
    g.triangle_plot(gdsamples, truths=truths, filled=True, title_limit=1)
    plt.savefig(path_plot_getdist, dpi=300, bbox_inches='tight')
    plt.clf()



def main(path2config):
    ## load the yaml parameters
    config = yaml.safe_load(open(path2config))
    ### input
    path_chain = config['path_chain']
    # path2config = config.get('path2config', None)
    ### output
    path_info = config.get('path_info', None)
    path_plot_run = config.get('path_plot_run', None)
    path_plot_trace = config.get('path_plot_trace', None)
    path_plot_corner = config.get('path_plot_corner', None)
    path_plot_getdist = config['path_plot_getdist']
    path_hod = config.get('path_hod', None)

    ## load & print results
    data = np.load(path_chain, allow_pickle=True)
    arr = data['res']
    res = arr.item()
    # with open(path_info, 'w') as f:
    #     print(res.summary(), file=f)
    # print(res.summary())
    res.summary()  # print summary to console
    ## max logl
    max_logl_idx = np.argmax(res.logl)
    max_logl_sample = res.samples[max_logl_idx]
    print('Max logl sample:', max_logl_sample)
    ## max logwt
    max_logwt_idx = np.argmax(res.logwt)
    max_logwt_sample = res.samples[max_logwt_idx]
    print('MAP:', max_logwt_sample)
    # truths = [12.78,13.94,0.17,1.07,0.55] # yuan's results
    truths = max_logwt_sample

    ## dyplot
    run_dyplot(path_plot_run, path_plot_trace, path_plot_corner, truths, res)

    ## getdist
    samples, weights = res.samples, res.importance_weights()
    run_getdist(samples, weights, truths, path_plot_getdist)

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
