import argparse, sys
import numpy as np
from getdist import loadMCSamples
from abacusnbody.hod.abacus_hod import AbacusHOD
from pathlib import Path
# THIS_REPO = Path(__file__).parent.parent
THIS_REPO = Path('/global/homes/s/siyizhao/projects/fihobi/')

src_dir = THIS_REPO / 'src'
if src_dir not in sys.path:
    sys.path.insert(0, str(src_dir))
from io_def import load_config, plot_style, path_to_clustering, write_catalogs
from abacus_helper import assign_hod, reset_fic, set_theory_density, compute_mock_and_multipole
from io_def import write_config
source_dir = THIS_REPO / 'hod-variation' / 'source'
if source_dir not in sys.path:
    sys.path.insert(0, str(source_dir))
from data_object import data_object
from chain_helper import bestfit_params

def parse_args():
    parser = argparse.ArgumentParser(description="Generate AbacusHOD mock from best-fit HOD parameters")
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration YAML file')
    parser.add_argument('--rsd', type=int, default=1, help='Whether to include RSD in the mock generation, (0: no rsd, 1: with rsd), default=1')
    args = parser.parse_args()
    return args

def prep_config(config):
    config_full=load_config(config)
    sim_params = config_full.get("sim_params", {})
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    fit_params = config_full.get("fit_params", {})
    # chain_params = config_full.get("chain_params",{})
    nthread = config_full.get("nthread", 32)
    return sim_params, HOD_params, clustering_params, data_params, fit_params, nthread

def gen_AbacusHOD_mock(bf, config_full):
    sim_params = config_full.get("sim_params", {})
    HOD_params = config_full.get("HOD_params", {})
    clustering_params = config_full.get("clustering_params", {})
    data_params = config_full.get("data_params", {})
    fit_params = config_full.get("fit_params", {})
    # chain_params = config_full.get("chain_params",{})
    nthread = config_full.get("nthread", 32)

    data_obj = data_object(data_params, HOD_params, clustering_params)
    tracers = list(fit_params.keys())
    tracer = tracers[0]
    ## generate AbacusHOD object
    ball_profiles = AbacusHOD(sim_params, HOD_params, clustering_params)
    assign_hod(ball_profiles, fit_params, bf)
    ngal_dict, fsat_dict = reset_fic(ball_profiles, tracers, data_obj.density_mean, nthread=nthread)
    density_bf = set_theory_density(ngal_dict, ball_profiles.params['Lbox']**3, data_obj.density_mean, tracers, nthread=nthread)
    
    mock_bf,clustering_bf=compute_mock_and_multipole(ball_profiles, nthread=nthread, out=False, verbose=True)
    out_root = sim_params.get('output_dir')

    prefix='MAP'
    if HOD_params['want_rsd']==False:
        prefix+='_realspace'
    elif HOD_params['want_rsd']==True:
        prefix+='_rsd'
    write_catalogs(ball_profiles, mock_bf, fit_params, out_root=out_root, prefix=prefix)
    
    loglike_bf = data_obj.compute_loglike(clustering_bf, density_bf)
    print("Best-fit loglike:", loglike_bf)
    
    # plot_all(data_obj,tracer,clustering_bf,out=chain_dir+chain_prefix+'bestfit_'+tracer+'.png', idxwp=np.arange(6,21), idxxi=np.arange(11,21))

    ## save bestfit clustering
    path2cluster  = path_to_clustering(sim_params, tracer=tracer, prefix=prefix)
    np.save(path2cluster, clustering_bf)
    print("Save bestfit clustering to:", path2cluster)
    return path2cluster

if __name__ == "__main__":
    args = parse_args()
    config = args.config
    rsd = args.rsd
    
    config_full=load_config(config)
    # config_full['sim_params']['sim_name'] = 'Abacus_pngbase_c302_ph001'
    # write_config(config_full, 'new_config.yaml')
    # !config=new_config.yaml
    # !python -m abacusnbody.hod.prepare_sim_profiles --path2config $config

    ## getdist
    chain_params = config_full.get("chain_params",{})
    chain_dir=chain_params['output_dir']
    chain_prefix=chain_params['chain_prefix']
    gdsamples = loadMCSamples(chain_dir+chain_prefix, settings={'ignore_rows':0.01})
    bf = bestfit_params(gdsamples)
 
    ## generate AbacusHOD mock
    print(rsd)
    if rsd==0:
       config_full['HOD_params']['want_rsd']=False
       print("Turn off RSD in mock generation.")
    
    path2cluster  = gen_AbacusHOD_mock(bf, config_full)
    
    ## save config used
    write_config(config_full, path2cluster.replace('.npy', '_config.yaml'))
    