import yaml
from pathlib import Path
THIS_REPO = Path(__file__).parent.parent
import numpy as np
import os

__all__ = ["z_to_tag", "def_OBSample",
    "ensure_dir", "write_script_to_file", "load_config", "write_config",
    "plot_style",
    "path_to_ObsClus", "path_to_AbacusSubsample", "path_to_HODchain", "path_to_mocks",
    "prefix_HOD", "path_to_HODconfigs", 
    "path_to_catalog", "path_to_clustering", "path_to_poles", 
    "write_catalogs", "read_catalog"]

def z_to_tag(z):
    return f"{float(z):.3f}".replace('.', 'p')

def def_OBSample(tracer: str, zmin: float, zmax: float)->dict:
    def tag_OBSample(tracer, zmin, zmax):
        return f"{tracer}_z{z_to_tag(zmin)}_{z_to_tag(zmax)}"
    obs = {
        "tracer": tracer,
        "zmin": zmin,
        "zmax": zmax,
        "tag": tag_OBSample(tracer, zmin, zmax)
        }
    return obs

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path

def write_script_to_file(script, filename, make_executable=False):
    if filename:
        outp = Path(filename)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(script, encoding="utf-8")
        print(f"[write] -> {filename}")
        if make_executable:
            outp.chmod(outp.stat().st_mode | 0o111)
    return script

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

def write_config(config, config_path):
    """
    Write the configuration dictionary to a YAML file.

    Parameters:
        config (dict): Configuration data to write.
        config_path (str): Path to the output YAML file.
    """
    try:
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f, sort_keys=False)
        print(f"[write] -> {config_path}")
    except Exception as e:
        raise RuntimeError(f"Error writing configuration file '{config_path}': {e}")

def plot_style() -> None:
    import matplotlib as mpl
    mpl.rc_file(THIS_REPO / 'fig' / 'matplotlibrc')

def path_to_ObsClus(verspec: str, version: str, mode: str='pycorr') -> Path:
    if mode=='pycorr':
        path = THIS_REPO / "data/clustering"
    elif mode=='forHOD':
        path = THIS_REPO / "data/HOD_fitting"
    else:
        raise ValueError(f"Unknown mode: {mode}")
    realpath = os.path.realpath(path / verspec / version / "PIP")
    return Path(realpath)

def path_to_AbacusSubsample():
    path = THIS_REPO / "data/AbacusSubsample"
    realpath = os.path.realpath(path)
    return Path(realpath)

def path_to_HODchain(work_dir: Path=None) -> Path:
    if work_dir is None:
        work_dir = THIS_REPO / "HIP"
        raise Warning("work_dir is not specified, using default 'HIP', recommended to specify to scratch.")
    realpath = os.path.realpath(work_dir / "HOD_chains")
    return Path(realpath)

def path_to_mocks(work_dir: Path=None) -> Path:
    if work_dir is None:
        work_dir = THIS_REPO / "HIP"
        raise Warning("work_dir is not specified, using default 'HIP', recommended to specify to scratch.")
    realpath = os.path.realpath(work_dir / "mocks")
    return Path(realpath)

def path_to_hip(work_dir: Path=None) -> Path:
    if work_dir is None:
        work_dir = THIS_REPO / "HIP"
        raise Warning("work_dir is not specified, using default 'HIP', recommended to specify to scratch.")
    realpath = os.path.realpath(work_dir)
    ensure_dir(realpath)
    return Path(realpath)

def prefix_HOD(hod):
    hod_model = hod.get('prefix', 'base')
    want_dv = hod.get('want_dv', False)
    Assembly = hod.get('Assembly', False)
    BiasENV = hod.get('BiasENV', False)
    if Assembly:
        hod_model += "-A"
    if BiasENV:
        hod_model += "-B"
    if want_dv:
        hod_model += "-dv"
    return hod_model

def path_to_HODconfigs(configs4HIP):
    cfgs = load_config(configs4HIP)
    galaxy = cfgs.get('galaxy', {})
    tracer = galaxy.get('tracer', 'QSO')
    ztag = galaxy.get('ztag', 'z6')
    fnl = cfgs.get('fnl', 100)
    hod = cfgs.get('HOD', {})
    hod_model = prefix_HOD(hod)
    current_dir = Path(__file__).resolve().parent
    path = current_dir.parent / "hod-variation" / "configs" / f"{tracer}-fnl{fnl}" / f"{ztag}_{hod_model}.yaml"
    print(f"Resolved HOD config path: {path}")
    return str(path)

def path_to_cat_dir(sim_params, tracer='QSO'):
    output_dir = Path(sim_params.get('output_dir', './'))
    sim_name = Path(sim_params['sim_name'])
    zsnap = float(sim_params.get('z_mock', 0.0))
    
    redshift_tag = z_to_tag(zsnap)
    
    mock_type = 'abacus_HF'
    version = 'DR2_v2.0'

    base_dir = os.path.join(output_dir, mock_type, version, sim_name, 'Boxes')
    # base_dir = path_to_mocks()
    tracer_dir = os.path.join(base_dir, tracer, f'z{redshift_tag}')
    ensure_dir(tracer_dir)
    return tracer_dir


def path_to_catalog(sim_params=None, config=None, tracer='QSO', prefix=None):
    '''
    sim_params: dict containing simulation parameters such as output_dir, sim_name, and z_mock.
    config: Path to a configuration file to load simulation parameters from. Only used if sim_params is None.
    '''
    tracer_dir = path_to_cat_dir(sim_params, tracer=tracer)
    sim_name = Path(sim_params['sim_name'])
    zsnap = float(sim_params.get('z_mock', 0.0))
    
    redshift_tag = z_to_tag(zsnap)
    
    mock_type = 'abacus_HF'
    version = 'DR2_v2.0'
    if prefix is None:
        fname = f"{mock_type}_{tracer}_{redshift_tag}_{version}_{sim_name}_clustering.dat.h5"
    else:
        fname = f"{mock_type}_{tracer}_{redshift_tag}_{version}_{sim_name}_{prefix}_clustering.dat.h5"
    outpath = os.path.join(tracer_dir, fname)
    return outpath

def path_to_clustering(sim_params, tracer='QSO', prefix=None):
    path_to_dir = path_to_cat_dir(sim_params=sim_params, tracer=tracer) 
    fname = f"{prefix}_clustering.npy" if prefix else "clustering.npy"
    clustering_path = os.path.join(path_to_dir, fname)
    return clustering_path   

def path_to_poles(sim_params, tracer='QSO', prefix=None):
    path_to_dir = path_to_cat_dir(sim_params=sim_params, tracer=tracer) 
    fname = f"{prefix}_pypower_poles.npy" if prefix else "pypower_poles.npy"
    path = os.path.join(path_to_dir, fname)
    return path   


def write_catalogs(Ball, mock_real: dict, fit_params: dict, out_root=None, prefix=None) -> None:
    from mpytools.catalog import Catalog

    # Pull meta directly from Ball
    sim_name = getattr(Ball, 'sim_name', None) or Ball.params.get('sim_name')
    if sim_name is None:
        raise KeyError("Ball.sim_name (or Ball.params['sim_name']) is required.")
    zsnap = float(Ball.params.get('z', 0.0))

    boxsize = float(Ball.params.get('Lbox'))
    velz2kms = float(Ball.params.get('velz2kms'))

    for tracer, cat in mock_real.items():

        # Fetch required arrays
        def fetch(name, default=None):
            if isinstance(cat, dict):
                return cat.get(name, default)
            elif hasattr(cat, 'dtype') and cat.dtype.names and name in cat.dtype.names:
                return cat[name]
            return default

        x  = fetch('x');  y  = fetch('y');  z  = fetch('z')
        vx = fetch('vx'); vy = fetch('vy'); vz = fetch('vz')
        if x is None or y is None or z is None:
            raise KeyError(f"Catalog for tracer {tracer} missing position arrays.")

        N = len(x)
        mass = fetch('mass', fetch('halo_mass'))
        if mass is None:
            mass = np.zeros(N, dtype='f8')
        gid  = fetch('id', fetch('halo_id'))
        if gid is None:
            gid = np.zeros(N, dtype='i8')
        vsmear = fetch('vsmear', None)
        if vsmear is None:
            vsmear = np.zeros(N, dtype='f8')
        Ncent = int(fetch('Ncent', 0) or 0)

        iscentral = np.zeros(N, dtype='i8')  # force i8; 1 for centrals, 0 otherwise
        if 0 <= Ncent <= N:
            iscentral[:Ncent] = 1

        # Enforce column dtypes explicitly
        data = {
            'X':         np.asarray(x,      dtype='f8'),
            'Y':         np.asarray(y,      dtype='f8'),
            'Z':         np.asarray(z,      dtype='f8'),
            'VX':        np.asarray(vx,     dtype='f8'),
            'VY':        np.asarray(vy,     dtype='f8'),
            'VZ':        np.asarray(vz,     dtype='f8'),
            'HALO_ID':   np.asarray(gid,    dtype='i8'),
            'MASS':      np.asarray(mass,   dtype='f8'),
            'VSMEAR':    np.asarray(vsmear, dtype='f8'),
            'ISCENTRAL': np.asarray(iscentral, dtype='i8'),
        }

        # Header with varying HOD params for this tracer (floats -> f8)
        varying = list(fit_params.get(tracer, {}).keys())
        hod = getattr(Ball, 'tracers', {}).get(tracer, {})
        hdr = {f"HOD_{k}": float(np.float64(hod[k])) for k in varying if k in hod}
        hdr['BOXSIZE'] = float(np.float64(boxsize))
        hdr['VELZ2KMS'] = float(np.float64(velz2kms))
        hdr['ZSNAP'] = float(np.float64(zsnap))
        hdr['REALIZATION'] = str(sim_name)  # not limited to 3 chars
        hdr['TRACER_TYPE'] = str(tracer)[:3].ljust(3)  # s3: 'LRG','ELG','QSO'

        # outpath = os.path.join(tracer_dir, fname)
        sim_params = {'output_dir': out_root, 'sim_name': sim_name, 'z_mock': zsnap}
        outpath = path_to_catalog(sim_params=sim_params, tracer=tracer, prefix=prefix)

        Catalog(data=data).write(outpath, header=hdr)
        print(f"[write] {tracer} -> {outpath}")

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