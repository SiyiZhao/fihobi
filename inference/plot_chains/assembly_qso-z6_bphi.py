import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain_bphi

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

names = ['bphi_QSO-z6_fNL100_base-dv', 'bphi_QSO-z6_fNL100_base-A-dv', 'bphi_QSO-z6_fNL100_base-B-dv']
labels=['z=3.0, base', 'z=3.0, base-A', 'z=3.0, base-B']
colors=[color[1], color[2], color[3]]
fn_out='out/compare_bphi_qso-z6_fnl100.png'

chains = ['/pscratch/sd/s/siyizhao/desilike/fit_PNG_bias/'+name+'/chain_zeus' for name in names]
compare_chain_bphi(chains, labels=labels, colors=colors, fn_out=fn_out)
