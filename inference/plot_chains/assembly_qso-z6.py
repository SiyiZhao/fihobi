import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

name='QSO-z6_fNL100_base-dv'
qso_z6_fNL100 = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
name='QSO-z6_fNL100_base-A-dv'
qso_z6_fNL100_base_A = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
compare_chain([qso_z6_fNL100, qso_z6_fNL100_base_A], labels=['z=3.0, fNL=100', 'z=3.0, fNL=100 base-A'], markers={'p':1.6}, colors=[color[3], color[4]], fn_out='out/compare_qso-z6_fnl100_base_dv_A.png')
