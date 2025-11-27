# python tests/logsigma.py

import numpy as np
import os, sys
sys.path.insert(0, os.path.abspath('../src'))
from chain_helper import chain

chain_LRG_z1 = chain(outdir='output/desi-dr2-hod/LRG-fnl100/z1_base', filename='/chain_v2_')

chain_LRG_z1.read_pmn()

def logsigma(params):
    sigma = params[2]
    return np.log10(sigma)

chain_LRG_z1.derive_new_params(derive_func=logsigma, new_para='logsigma', new_para_label='\log \sigma', filename='/chain_v2_logsigma_')

chain_LRG_z1.plot_result(plot_path='output/tests/logsigma_triangle_plot.png')