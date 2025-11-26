# here we compare 2 chains from different fits with different EZmock numbers and dk

import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

names = ['QSO-z1_fNL100_base', 'QSO-z1_fNL100_base_n500']
labels=['1000 EZmocks, default dk', '500 EZmocks, dk=0.005']
colors=["#1b1b1b", "#D55E00",]
fn_out='out/compare_nEZmocks.png'

chains = ['out/fit_PNG_bias_v2/'+name+'/chain_zeus' for name in names]
compare_chain(chains, labels=labels, markers={'p':1.6}, colors=colors, fn_out=fn_out)
