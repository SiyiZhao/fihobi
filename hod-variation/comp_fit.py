# -*- coding: utf-8 -*-
"""
Python version of comp_fit.ipynb, we recommend using the notebook version instead.
Workspace: projects/fihobi/hod-variation/
"""

import numpy as np
import os, sys
from pathlib import Path
THIS_REPO = Path(__file__).parent.parent.parent 
src_dir = THIS_REPO / 'src'
if src_dir not in sys.path:
    sys.path.insert(0, str(src_dir))
from io_def import load_config

source_dir = THIS_REPO / 'hod-variation' / 'source'
if source_dir not in sys.path:
    sys.path.insert(0, str(source_dir))
from post_helpers import read_bf_clus, plot_all
from data_object import data_object
from chain_helper import compare_chain


def compare_clustering(configs, labels=None, colors=None, fn_out=None):
    clus_list = [read_bf_clus(load_config(cfg)) for cfg in configs]
    clus_baseline = clus_list[0]
    clus_others = clus_list[1:]
    tracer = 'QSO'
    
    config_full=load_config(configs[0])
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    data_obj = data_object(data_params, HOD_params, clustering_params)
    
    plot_all(data_obj, tracer, clus_baseline, idxwp=np.arange(6,21), idxxi=np.arange(11,21), clustering_other=clus_others, labels=labels, colors=colors, out=fn_out)

if __name__ == "__main__":
    # configs = ['configs/QSO-fnl30/z6_base-dv.yaml', 'configs/QSO-fnl100/z6_base.yaml', 'configs/QSO-fnl100/z6_base-dv.yaml']
    # labels = ['c300, w/ dv', 'c302, w/o dv', 'c302, w/ dv']
    # colors = ['black', "#1458C5", "#C44536"]
    # chains_out = 'output/comp_chains_z6.png'
    # clus_out = 'output/comp_clustering_z6.png'
    # tags = ['z1', 'z6']
    tags = ['z5']
    # tags = ['z1', 'z2', 'z3', 'z4', 'z5', 'z6']
    for tag in tags:
        configs = [f'configs/QSO-fnl100/{tag}_base-dv.yaml', f'configs/QSO-fnl100/{tag}_base.yaml', f'configs/QSO-fnl100/{tag}_base-A-dv.yaml']#, f'configs/QSO-fnl100/{tag}_base-B-dv.yaml']
        labels = ['c302(fnl=100), w/ dv', 'c302(fnl=100), w/o dv', 'c302(fnl=100), w/ dv, c']#, 'c302(fnl=100), w/ dv, $\delta$']
        colors = ['black', "#1458C5", "#C44536"]#, "#28A745"]
        chains_out = f'output/comp_chains_{tag}.png'
        clus_out = f'output/comp_clustering_{tag}.png'
        ## compare chains
        compare_chain(configs, labels=labels, colors=colors, fn_out=chains_out)
        ## compare clustering
        compare_clustering(configs, labels=labels, colors=colors, fn_out=clus_out)


    # fn_z2 = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl30/z2_base-dv/base-dv'
    # fn_z2_dv = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl30/z2_base-dv/chain_rp6s11_'
    # labels = ['c300, w/ dv, rp3s8', 'c300, w/ dv, rp6s11']
    # ## compare chains
    # fn_out = 'output/comp_chains_z2.png'
    # compare_chain([fn_z2, fn_z2_dv], labels=labels, colors=['black', "#C44536"], fn_out=fn_out)
