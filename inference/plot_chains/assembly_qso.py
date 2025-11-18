import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

names = ['QSO-z1_fNL100_base-dv', 'QSO-z1_fNL100_base-A-dv',
         'QSO-z6_fNL100_base-dv', 'QSO-z6_fNL100_base-A-dv']
labels=['z=0.95, base', 'z=0.95, base-A', 'z=3.0, base', 'z=3.0, base-A']
colors=[color[1], color[2], color[3], color[5]]
fn_out='out/compare_A_qso_fnl100_base_dv.png'

chains = ['/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus' for name in names]
compare_chain(chains, labels=labels, markers={'p':1.6}, colors=colors, fn_out=fn_out)