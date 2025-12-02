# python tests/logalpha.py

import numpy as np
import os, sys
sys.path.insert(0, os.path.abspath('../src'))
from chain_helper import chain

chain_ = chain(outdir='output/desi-dr2-hod/QSO-fnl100/z6_base/', filename='chain_v2_')

chain_.read_pmn()

def logalpha(params):
    alpha = params[4]
    return np.log10(alpha)

def logalpha_c(params):
    alpha_c = params[5]
    return np.log10(alpha_c)

def logalpha_s(params):
    alpha_s = params[6]
    return np.log10(alpha_s)

chain_.derive_new_params(derive_func=logalpha, new_para='logalpha', new_para_label='\log \\alpha', filename='chain_v2_logalpha_')
chain_.derive_new_params(derive_func=logalpha_c, new_para='logalpha_c', new_para_label='\log \\alpha_{c}', filename='chain_v2_logalpha_c_')
chain_.derive_new_params(derive_func=logalpha_s, new_para='logalpha_s', new_para_label='\log \\alpha_{s}', filename='chain_v2_logalpha_s_')
chain_.plot_result(plot_path='output/tests/logalpha_triangle_plot.png')