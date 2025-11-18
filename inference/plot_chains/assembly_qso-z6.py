import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

names = ['QSO-z6_fNL100_base-dv', 'QSO-z6_fNL100_base-A-dv', 'QSO-z6_fNL100_base-B-dv']#, 'QSO-z6_fNL100_base-B-dv_ez300']
labels=['z=3.0, base', 'z=3.0, base-A', 'z=3.0, base-B']#, 'z=3.0, base-B, ez300']
colors=[color[1], color[2], color[3]]#, color[4]]
fn_out='out/compare_qso-z6_fnl100.png'

chains = ['/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus' for name in names]
compare_chain(chains, labels=labels, markers={'p':1.6}, colors=colors, fn_out=fn_out)
