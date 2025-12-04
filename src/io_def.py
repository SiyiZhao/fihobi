import yaml
from pathlib import Path
import numpy as np
import os

def load_config(config_path):
    """
    Load and parse the YAML configuration file.

    Parameters:
        config_path (str): Path to the YAML configuration file.
    
    Returns:
        dict: Configuration data parsed from YAML.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise RuntimeError(f"Error loading configuration file '{config_path}': {e}")

def path_to_catalog(config, tracer='QSO', custom_prefix=None):
    config_full=load_config(config)
    sim_params = config_full.get("sim_params", {})
    output_dir = Path(sim_params.get('output_dir', './'))
    sim_name = Path(sim_params['sim_name'])
    zsnap = float(sim_params.get('z_mock', 0.0))
    def z_to_tag(z):
        return f"{float(z):.3f}".replace('.', 'p')
    redshift_tag = z_to_tag(zsnap)
    
    mock_type = 'abacus_HF'
    version = 'DR2_v2.0'

    base_dir = os.path.join(output_dir, mock_type, version, sim_name, 'Boxes')
    tracer_dir = os.path.join(base_dir, tracer)
    if custom_prefix is None:
        fname = f"{mock_type}_{tracer}_{redshift_tag}_{version}_{sim_name}_clustering.dat.h5"
    else:
        fname = f"{mock_type}_{tracer}_{redshift_tag}_{version}_{sim_name}_{custom_prefix}_clustering.dat.h5"
    outpath = os.path.join(tracer_dir, fname)
    return outpath

def path_to_clustering(config, prefix=None):
    path_to_cat = path_to_catalog(config) 
    path_to_dir = os.path.dirname(path_to_cat)
    fname = f"{prefix}_clustering.npy" if prefix else "clustering.npy"
    clustering_path = os.path.join(path_to_dir, fname)
    return clustering_path   

def path_to_poles(config, prefix=None):
    path_to_cat = path_to_catalog(config) 
    path_to_dir = os.path.dirname(path_to_cat)
    fname = f"{prefix}_pypower_poles.npy" if prefix else "pypower_poles.npy"
    path = os.path.join(path_to_dir, fname)
    return path   

def read_catalog(path2mock: str) -> np.ndarray:
    from mockfactory import Catalog
    
    cat=Catalog.read(path2mock)
    # boxsize = cat.headers['BOXSIZE']
    # z_mock = cat.headers['ZSNAP']
    x = cat['X']
    y = cat['Y']
    z = cat['Z']
    pos = np.vstack((x, y, z)).T
    return pos