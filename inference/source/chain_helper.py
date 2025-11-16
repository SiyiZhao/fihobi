# -*- coding: utf-8 -*-
"""
Workspace: projects/fihobi/inference/
"""

import yaml
from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rc_file('../fig/matplotlibrc')


def load_chain_prefix(fn):
    # Load YAML configuration.
    with open(fn, 'r') as f:
        config = yaml.safe_load(f) 
    chain_params = config['chain_params']
    chain_prefix = chain_params['chain_prefix']
    output_dir = chain_params['output_dir']
    return output_dir+chain_prefix
    

def compare_chain(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], markers={'p':1.0}, fn_out=None):
    samples_all = []
    for fn in fn_all:
        samples = loadMCSamples(fn, settings={'ignore_rows':0.01})
        samples_all.append(samples)
    
    g = plots.get_subplot_plotter()
    g.settings.legend_fontsize = 30
    g.settings.axes_labelsize = 30
    g.settings.axes_fontsize = 20
    g.settings.linewidth_contour = 2.0   # 改 contour 线条宽度
    g.settings.linewidth = 2.0           # 改 1D 曲线的线宽
    g.triangle_plot(samples_all, params=['p', 'b1', 'sn0', 'sigmas'], markers=markers, legend_labels=labels, legend_loc='upper right', filled=False, contour_colors=colors)
    if fn_out:
        plt.savefig(fn_out, bbox_inches='tight')
        print(f"Saved figure to {fn_out}")
    else:
        plt.show()
        