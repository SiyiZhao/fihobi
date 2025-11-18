import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

names = ['QSO-z1_fNL100_base-dv', 'QSO-z1_fNL100_base-A-dv', 'QSO-z1_fNL100_base-B-dv']
labels=['z=0.95, base', 'z=0.95, base-A', 'z=0.95, base-B']
colors=[color[1], color[2], color[3]]
fn_out='out/compare_qso-z1_fnl100.png'

chains = ['/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus' for name in names]
compare_chain(chains, labels=labels, markers={'p':1.6}, colors=colors, fn_out=fn_out)