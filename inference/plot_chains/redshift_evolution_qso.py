import sys
sys.path.insert(0, 'source')
from chain_helper import compare_chain

color = ["#1b1b1b", "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]

# name='QSO-z4_fNL30_base-dv'
# qso_z4_fNL30 = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
name='QSO-z1_fNL100_base-dv'
qso_z1_fNL100 = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
name='QSO-z6_fNL100_base-dv'
qso_z6_fNL100 = '/pscratch/sd/s/siyizhao/desilike/fit_p/'+name+'/chain_zeus'
# compare_chain([qso_z4_fNL30, qso_z1_fNL100, qso_z6_fNL100], labels=['z=2.0, fNL=30', 'z=0.95, fNL=100', 'z=3.0, fNL=100'], markers={'p':1.6}, colors=[color[1], color[2], color[3]])
compare_chain([qso_z1_fNL100, qso_z6_fNL100], labels=['z=0.95, fNL=100', 'z=3.0, fNL=100'], markers={'p':1.6}, colors=[color[2], color[3]], fn_out='out/compare_redshift_evolution_qso.png')
