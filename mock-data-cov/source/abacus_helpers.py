import yaml
from pathlib import Path

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
