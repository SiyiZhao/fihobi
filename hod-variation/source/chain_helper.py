# -*- coding: utf-8 -*-
"""
Workspace: projects/fihobi/
"""

import yaml
import numpy as np
from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('fig/matplotlibrc')


def load_chain_prefix(fn):
    # Load YAML configuration.
    with open(fn, 'r') as f:
        config = yaml.safe_load(f) 
    chain_params = config['chain_params']
    chain_prefix = chain_params['chain_prefix']
    output_dir = chain_params['output_dir']
    return output_dir+chain_prefix

def bestfit_params(gdsamples):
    ## max weight
    samples, weights = gdsamples.samples, gdsamples.weights
    max_weight_idx = np.argmax(weights)
    max_logwt_sample = samples[max_weight_idx]
    print('MAP:', max_logwt_sample)
    return max_logwt_sample

def compare_chain(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], fn_out=None):
    samples_all = []
    params = []
    param_limits = {}
    bestfits = {}
    for fn in fn_all:
        chain_prefix = load_chain_prefix(fn)
        samples = loadMCSamples(chain_prefix, settings={'ignore_rows':0.01})
        samples_all.append(samples)
        # Get parameter names and update limits
        pnames = samples.getParamNames().list()
        for name in pnames:
            if name not in params:
                params.append(name)
                bestfits[name] = []
            # Update parameter limits
            lo, hi = samples.getLower(name), samples.getUpper(name)
            if name in param_limits:
                cur_lo, cur_hi = param_limits[name]
                param_limits[name] = (min(cur_lo, lo), max(cur_hi, hi))
            else:
                param_limits[name] = (lo, hi)
        # # Get best-fit values
        # bf = bestfit_params(samples)
        # for i, name in enumerate(pnames):
        #     bestfits[name].append(bf[i])
    g = plots.get_subplot_plotter()
    g.settings.legend_fontsize = 30
    g.settings.axes_labelsize = 30
    g.settings.axes_fontsize = 20
    g.settings.linewidth_contour = 2.0   # 改 contour 线条宽度
    g.settings.linewidth = 2.0           # 改 1D 曲线的线宽
    # marker_args = [{'color': color, 'linestyle': '--', 'linewidth': 3.0, 'label': labels[i]+' - MAP'} for i, color in enumerate(colors)]
    g.triangle_plot(
        samples_all,
        params=params,
        param_limits=param_limits,
        filled=False,
        contour_colors=colors,
        # markers=bestfits,
        # marker_args=marker_args,
        legend_labels=labels,
        legend_loc='upper right',
    )
    if fn_out:
        plt.savefig(fn_out, bbox_inches='tight')
        print(f"Saved figure to {fn_out}")
    else:
        plt.show()