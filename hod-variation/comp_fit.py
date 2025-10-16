# -*- coding: utf-8 -*-
"""
Python version of comp_fit.ipynb, we recommend using the notebook version instead.
Workspace: projects/fihobi/hod-variation/
"""

import numpy as np
import os, sys
current_dir = os.getcwd()
source_dir = os.path.join(current_dir,"source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from post_helpers import load_config, read_bf_clus, plot_all
from data_object import data_object
from chain_helper import compare_chain


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




    fn_z2 = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl30/z2_base-dv/base-dv'
    fn_z2_dv = '/pscratch/sd/s/siyizhao/desi-dr2-hod/QSO-fnl30/z2_base-dv/chain_rp6s11_'
    labels = ['c300, w/ dv, rp3s8', 'c300, w/ dv, rp6s11']
    ## compare chains
    fn_out = 'output/comp_chains_z2.png'
    compare_chain([fn_z2, fn_z2_dv], labels=labels, colors=['black', "#C44536"], fn_out=fn_out)
