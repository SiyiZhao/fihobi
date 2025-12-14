import argparse
import numpy as np
from getdist import loadMCSamples, plots
from getdist import MCSamples
from abacusnbody.hod.abacus_hod import AbacusHOD
import os, sys
sys.path.insert(0, 'source')
from post_helpers import compute_all
sys.path.insert(0, '../src')
from io_def import load_config, plot_style, path_to_HODconfigs, path_to_catalog, write_catalogs, path_to_clustering
from abacus_helper import build_param_mapping, assign_hod, reset_fic
plot_style()

## load config
parser = argparse.ArgumentParser()
parser.add_argument('--cfgs4HIP', type=str, default='HIP.yaml', help='Path to the HIP config file, do not provide --config.')
parser.add_argument('--config', type=str, help='Path to the HOD config file')
args = parser.parse_args()

if args.config is None:
    cfgs4HIP = args.cfgs4HIP
    cfgs_HIP = load_config(cfgs4HIP)
    cfgs_sample = cfgs_HIP.get('sampleHOD', {})
    config = path_to_HODconfigs(cfgs4HIP)
else:
    config = args.config
    cfgs_sample = {}
config_full=load_config(config)
sim_params = config_full.get("sim_params", {})
HOD_params = config_full.get("HOD_params", {})
clustering_params = config_full.get("clustering_params", {})
chain_params = config_full.get("chain_params",{})
fit_params = config_full.get("fit_params", {})
data_params = config_full.get("data_params", {})
density_mean = data_params.get("tracer_density_mean", {})
nthread = config_full.get("nthread", 32)
out_root = sim_params.get('output_dir')

chain_dir=chain_params['output_dir']
chain_prefix=chain_params['chain_prefix']

### load chain samples and compute mean and covariance
gdsamples = loadMCSamples(chain_dir+chain_prefix, settings={'ignore_rows':0.01})
mean = gdsamples.getMeans()
print("Mean parameters:", mean)
cov = gdsamples.getCovMat().matrix

### function to sample from multivariate Gaussian
def sample_multivariate_gaussian(mean, cov, nsamples=10000, seed=None):
    rng = np.random.default_rng(seed)
    samples = rng.multivariate_normal(mean, cov, size=nsamples)
    return samples

### generate 100 samples to plot counterplots
num = 100
samples = sample_multivariate_gaussian(mean, cov, nsamples=num)
pnames = gdsamples.getParamNames().list()
mgsamples = MCSamples(samples=samples, names=pnames)
g = plots.get_subplot_plotter()
g.triangle_plot([gdsamples, mgsamples], legend_labels=['Original', 'Multivariate Gaussian'], filled=False, title_limit=2)
# g.export(chain_dir+chain_prefix+'multivariate_gaussian.png')

### generate 10 samples to use in HOD modeling
num = cfgs_sample.get("num", 10)
samples = sample_multivariate_gaussian(mean, cov, nsamples=num, seed=42)
# g.triangle_plot(gdsamples, filled=False, title_limit=1)
comap = cfgs_sample.get("cmap", "viridis")
idx = np.arange(num)
nparam = len(pnames)
for i in range(nparam):
    for j in range(i):
        ax = g.subplots[i][j]
        ax.scatter(samples[:, j], samples[:, i], c=idx, cmap=comap, s=10, edgecolors='k', label=f'i{idx}')
np.savetxt(chain_dir+chain_prefix+'multivariate_gaussian_samples.txt', samples, header=','.join(pnames))
g_out = chain_dir+chain_prefix+'multivariate_gaussian_scatter.png'
g.export(g_out)
print(f"Generated {num} samples for HOD modeling, plot saved in {g_out}.")

### generate AbacusHOD mocks for each sample
param_mapping = build_param_mapping(fit_params)
Ball = AbacusHOD(sim_params, HOD_params, clustering_params)

path2cat = path_to_catalog(config=config)
path2dir = os.path.dirname(path2cat)
for i, sample in enumerate(samples):
    sample[6] = 10**sample[6]  # convert log alpha_s to alpha_s
    print(f"Sampled parameters {i}:", sample)
    assign_hod(Ball, param_mapping, sample)
    reset_fic(Ball, HOD_params, density_mean, nthread=nthread)
    mock, clustering_rsd  = compute_all(Ball, nthread)
    ## save mock h5
    write_catalogs(Ball, mock, fit_params, out_root=out_root, custom_prefix=f'r{i}')
    ## save clustering ASCII
    path2cluster = path_to_clustering(config, prefix=f'r{i}')
    np.save(path2cluster, clustering_rsd)
    print(f"[write] clustering for sample {i} to {path2cluster}")
print("All done.")
