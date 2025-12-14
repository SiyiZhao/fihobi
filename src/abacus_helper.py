from pathlib import Path
import numpy as np
import sys, os
sys.path.insert(0, os.path.expanduser('~/lib/'))
from abacusnbody.hod.abacus_hod import AbacusHOD
from io_def import load_config

__all__ = [
    "find_zsnap",
    "set_sim_params",
    "set_HOD_tracer",
    "set_HOD_params",
    "set_clustering_params",
    "build_param_mapping",
    "get_enabled_tracers",
    "assign_hod",
    "reset_fic",
    "set_theory_density",
    "generate_AbacusHOD_mock",
    "path_to_mock_dir"
]

def find_zsnap(zeff: float | dict[str, float]) -> float:
    """
    Find the nearest snapshot redshift in AbacusSummit to the effective redshift(s).
    """
    primary = [
        3.0, 2.5, 2.0, 1.7, 1.4, 1.1, 0.8, 0.5,
        0.4, 0.3, 0.2, 0.1, 0.0
    ]
    secondary = [
        0.15, 0.25, 0.35, 0.45, 0.575, 0.65, 0.725, 0.875,
        0.95, 1.025, 1.175, 1.25, 1.325, 1.475, 1.55, 1.625,
        1.85, 2.25, 2.75, 3.0, 5.0, 8.0
    ]
    all_values = primary + secondary
    def find_nearest(v: float) -> float:
        return min(all_values, key=lambda t: abs(t - v))
    if isinstance(zeff, dict):
        zsnaps = [find_nearest(v) for v in zeff.values()]
        unique = set(zsnaps)
        if len(unique) > 1:
            raise ValueError(f"Multiple zsnap values found: {unique}")
        zsnap = unique.pop()
    else:
        zsnap = find_nearest(zeff)
    return float(zsnap)

def set_sim_params(
    sim_name: str,
    z_mock: float,
    output_dir: str='./', 
    subsample_dir: str='./',
    sim_dir: str='/global/cfs/projectdirs/desi/cosmosim/Abacus/',
    cleaned_halos: bool=True,
    force_mt: bool=True,
) -> dict:
    cfg_sim = {
        'cleaned_halos': cleaned_halos,
        'output_dir': str(output_dir),
        'sim_dir': str(sim_dir),
        'sim_name': sim_name,
        'subsample_dir': str(subsample_dir)+'/',
        'z_mock': z_mock,
        'force_mt': force_mt
    }
    return cfg_sim

def set_HOD_tracer(
    logM_cut: float,
    logM1: float,
    sigma: float,
    alpha: float,
    kappa: float,
    alpha_c: float=0.0,
    alpha_s: float=1.0,
    Acent: float=0.0,
    Asat: float=0.0,
    Bcent: float=0.0,
    Bsat: float=0.0,
    ic: float=1.0,
    profile_code: int=1,
) -> dict:
    hod_tracer = {
        'logM_cut': logM_cut,
        'logM1': logM1,
        'sigma': sigma,
        'alpha': alpha,
        'kappa': kappa,
        'alpha_c': alpha_c,
        'alpha_s': alpha_s,
        'ic': ic,
        'profile_code': profile_code
    }
    return hod_tracer

def set_HOD_params(
    tracers: dict,
    use_particles: bool=False,
    use_profiles: bool=True,
    want_AB: bool=True,
    want_rsd: bool=True,
    want_dv: bool=False,
    dv_draw: dict | None=None, 
):
    tracer_flags = {'ELG': False, 'LRG': False, 'QSO': False}
    for tracer in tracers.keys():
        tracer_flags[tracer] = True
    cfg_HOD = {
        'tracer_flags': tracer_flags,
        'use_particles': use_particles,
        'use_profiles': use_profiles,
        'want_AB': want_AB,
        'want_rsd': want_rsd,
        'want_dv': want_dv,
        'write_to_disk': False,
    }
    if dv_draw is not None:
        for key in dv_draw.keys():
            print(f"dv_draw[{key}] = {dv_draw[key]}")
            key_i = key[0] # first letter of tracer, 'Q' for 'QSO'
            cfg_HOD[f'dv_draw_{key_i}'] = dv_draw[key]
    for t in tracers:
        cfg_HOD[f'{t}_params'] = tracers[t]
    return cfg_HOD

def set_clustering_params():
    cfg_clus = {
        'bin_params':{
            'logmax': 1.5,
            'logmin': -1.0,
            'nbins': 15
        },
        'clustering_type': 'all',
        'pi_bin_size': 40,
        'pimax': 40,
    }
    return cfg_clus

def build_param_mapping(fit_params: dict) -> dict:
    """
    from fit_params, build a mapping from (tracer, param) to index in the parameter vector.
    
    eg: input {'QSO': {'logMmin': [0, 12.0, 14.0, 'flat'], 'sigma_logM': [1, 0.1, 1.0, 'flat']}, output {'QSO': {'logMmin': 0, 'sigma_logM': 1}}
    
    Credit: https://github.com/ahnyu/hod-variation/blob/main/source/io_helpers.py
    """
    entries = []  # (provided_index, tracer, param)
    for tracer, params in fit_params.items():
        for param, values in params.items():
            provided_index = values[0]
            entries.append((int(provided_index), tracer, param))
    entries.sort(key=lambda t: t[0])
    pos = {pid: i for i, (pid, _, _) in enumerate(entries)}
    if len(pos) != len(entries):
        raise ValueError("Duplicate provided_index detected in fit_params; indices must be unique.")
    mapping = {}
    for pid, tracer, param in entries:
        mapping.setdefault(tracer, {})[param] = pos[pid]
    return mapping


def get_enabled_tracers(HOD_params: dict) -> list:
    flags = HOD_params.get('tracer_flags', {}) or {}
    return [t for t, f in flags.items() if bool(f)] if isinstance(flags, dict) else []

def assign_hod(Ball, fit_params: dict, params: np.ndarray) -> None:
    param_mapping = build_param_mapping(fit_params)
    for tracer in param_mapping:
        for pname, idx in param_mapping[tracer].items():
            if fit_params[tracer][pname][3] == 'log':
                Ball.tracers[tracer][pname] = 10**float(params[idx])
            else:   
                Ball.tracers[tracer][pname] = float(params[idx])

def reset_fic(Ball, HOD_params: dict, density_mean: dict, nthread: int = 32) -> None:
    tracers = get_enabled_tracers(HOD_params)
    # Reset 'ic' and compute theoretical number density.
    for tracer in tracers:
        Ball.tracers[tracer]['ic'] = 1
    ngal_dict, fsat_dict = Ball.compute_ngal(Nthread=nthread)
    # Update 'ic' for non-ELG tracers.
    box_volume = Ball.params['Lbox']**3
    for tracer in tracers:
        if tracer == 'LRG':
            ngal = ngal_dict[tracer]
            if ngal > density_mean[tracer] * box_volume:
                Ball.tracers[tracer]['ic'] = density_mean[tracer] * box_volume / ngal
        else:
            ngal = ngal_dict[tracer]
            if ngal > 0.001 * box_volume:
                Ball.tracers[tracer]['ic'] = 0.001 * box_volume / ngal
    return Ball, ngal_dict, fsat_dict

def set_theory_density(ngal_dict, box_volume, density_mean, tracers, nthread=32):
    """
    If the data mean density is lower than the theoretical density, set the theoretical density to the data mean.
    """
    theory_density_dict = {}    
    for tracer in tracers:
        ngal = ngal_dict[tracer]
        data_mean = density_mean[tracer]
        if data_mean < ngal / box_volume:
            theory_density_dict[tracer] = data_mean
            print(f"Set theoretical density of {tracer} to data mean: {data_mean}")
        else:
            theory_density_dict[tracer] = ngal / box_volume
    return theory_density_dict

# def generate_AbacusHOD_config():
#     sim_params = set_sim_params(sim_name=sim_name, z_mock=z_mock, output_dir=output_dir, subsample_dir=subsample_dir)
#     hod_QSO = set_HOD_tracer(logM_cut=13.0, logM1=14.0, sigma=0.5, alpha=1.0, kappa=0.0, alpha_c=0.0, alpha_s=0.0, ic=0.0)
#     tracers = {'QSO': hod_QSO}
#     HOD_params = set_HOD_params(tracers)
#     config = {
#         'sim_params': sim_params,
#         'HOD_params': HOD_params
#     }
#     return config

def generate_AbacusHOD_mock():
    # Ball = AbacusHOD(sim_params, HOD_params, clustering_params)
    # mock_dict = Ball.run_hod(tracers=Ball.tracers, Nthread=nthread, verbose=verbose)
    return None

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

