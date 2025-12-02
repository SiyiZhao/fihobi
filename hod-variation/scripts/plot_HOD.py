# python scripts/plot_HOD.py 

from getdist import loadMCSamples
import sys
sys.path.insert(0, "source")
from plot_hod import plot_HOD_stat

chain_dir='output/desi-dr2-hod/LRG-fnl100/z1_base/'
chain_prefix='chain_v2_'
path = 'output/tests/LRG_z1_base_HOD.png'

gdsamples = loadMCSamples(chain_dir+chain_prefix, settings={'ignore_rows':0.01})
samples, weights = gdsamples.samples, gdsamples.weights
fig, ax = plot_HOD_stat(samples, weights, path=path, want_tot=False)
