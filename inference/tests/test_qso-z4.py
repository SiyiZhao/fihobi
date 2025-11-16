import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

name='QSO-z4_fNL30_base'
qso_base = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
name='QSO-z4_fNL30_base-dv'
qso_base_dv = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
name='QSO-z4rp6s11_fNL30_base-dv'
qso_rp6s11_dv = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
compare_chain([qso_base, qso_base_dv, qso_rp6s11_dv], labels=['w/o dv', 'w dv', 'w dv, rp6s11'], markers={'p':1.6}, colors=[color[1], color[2], color[3]], fn_out='out/compare_qso-z4_fnl30_base_dv_rp6s11.png')
