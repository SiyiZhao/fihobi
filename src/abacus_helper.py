from pathlib import Path
import numpy as np
from io_def import load_config

def path_to_mock_dir(config):
    config_full=load_config(config)
    sim_params = config_full.get("sim_params", {})
    HOD_params = config_full.get("HOD_params", {})
    z_mock = sim_params['z_mock']
    output_dir = Path(sim_params.get('output_dir', './'))
    simname = Path(sim_params['sim_name'])
    mock_dir = output_dir / simname / ('z%4.3f' % z_mock)
    want_rsd = HOD_params['want_rsd']
    want_dv = HOD_params.get('want_dv', False)
    if want_rsd:
        rsd_string = '_rsd'
        if want_dv:
            rsd_string += '_dv'
    else:
        rsd_string = ''
    outdir = (mock_dir) / ('galaxies' + rsd_string)
    return outdir

def read_AbacusHOD_cat(fname):
    '''
    Read AbacusHOD catalog file.
    Return: x, y, z arrays in Mpc/h
    '''
    print(f"Loading mock from {fname}")
    with open(fname, 'r') as f:
        it = iter(f)
        for line in it:
            if not line.lstrip().startswith('#'):
                break
        data = np.loadtxt(it)
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]
    return x, y, z

