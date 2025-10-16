# -*- coding: utf-8 -*-
"""
Workspace: projects/fihobi/hod-variation/
"""

import numpy as np
import matplotlib.pyplot as plt
from getdist import loadMCSamples, plots
import os, sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from post_helpers import load_config, plot_all
from data_object import data_object

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

def compare_chain(fn_all, labels=['chain1', 'chain2'], colors=['red', 'blue'], fn_out=None):
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
    g.triangle_plot(samples_all, legend_labels=labels, filled=False, contour_colors=colors)
    if fn_out:
        plt.savefig(fn_out, bbox_inches='tight')
    else:
        plt.show()
        
def read_bf_clus(config, tracer='QSO'):
    'read the best-fit clustering measured by post.py, input: config file'
    config_full=load_config(config)
    sim_params = config_full['sim_params']
    hod_params = config_full['HOD_params']
    output_dir = sim_params['output_dir']
    sim_name = sim_params['sim_name']
    z_mock = sim_params['z_mock']
    mock_dir = output_dir + sim_name + f'/z{z_mock:.3f}'
    want_rsd = hod_params.get('want_rsd', False)
    want_dv = hod_params.get('want_dv', False)
    if want_rsd:
        rsd_string = '_rsd'
        if want_dv:
            rsd_string += '_dv'
    else:
        rsd_string = ''
    outdir = mock_dir + '/galaxies' + rsd_string
    path2cluster = outdir + f'/{tracer}s_clustering.npy'
    clustering_bf = np.load(path2cluster, allow_pickle=True).item()
    return clustering_bf
        
if __name__ == "__main__":
    fn_z4 = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl30/z4_base/base'
    fn_z4_dv = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl30/z4_base-dv/chain_'
    labels = ['c300, w/o dv', 'c300, w dv']
    ## compare chains
    fn_out = 'output/comp_chains_z4.png'
    compare_chain([fn_z4, fn_z4_dv], labels=labels, colors=['black', "#C44536"], fn_out=fn_out)

    ## compare clustering
    config_base = 'configs/QSO-fnl30/z4_base.yaml'
    cf_base = read_bf_clus(config_base)
    config_dv = 'configs/QSO-fnl30/z4_base-dv.yaml'
    cf_dv = read_bf_clus(config_dv)
    fn_out = 'output/comp_clustering_z4.png'
    clus_baseline = cf_base 
    clus_others = [cf_dv]
    tracer = 'QSO'
    
    config_full=load_config(config_base)
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    data_obj = data_object(data_params, HOD_params, clustering_params)
    
    plot_all(data_obj, tracer, clus_baseline, idxwp=np.arange(3,21), idxxi=np.arange(8,21), clustering_other=clus_others, labels=labels, out=fn_out)
   