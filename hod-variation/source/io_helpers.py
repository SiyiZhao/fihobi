# Credit: https://github.com/ahnyu/hod-variation/blob/main/source/io_helpers.py, modified by Siyi Zhao

import os
import glob
import numpy as np
from mpytools.catalog import Catalog

__all__ = [
    'ensure_dir',
    'build_param_mapping',
    'assign_hod',
    'get_enabled_tracers',
    'find_best_opt_sample',
    'extract_wp_xi',
    'save_clustering_ascii',
]

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def build_param_mapping(fit_params: dict) -> dict:

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


def assign_hod(Ball, param_mapping: dict, params: np.ndarray) -> None:
    for tracer in param_mapping:
        for pname, idx in param_mapping[tracer].items():
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

def theory_density(Ball, data_obj, tracers, nthread=32):
    box_volume = Ball.params['Lbox']**3
    theory_density_dict = {}
    ngal_dict, fsat_dict = Ball.compute_ngal(Nthread=nthread)
    for tracer in tracers:
        ngal = ngal_dict[tracer]
        data_mean = data_obj.density_mean[tracer]
        if data_mean < ngal / box_volume:
            theory_density_dict[tracer] = data_mean
            print(f"Set theoretical density of {tracer} to data mean: {data_mean}")
        else:
            theory_density_dict[tracer] = ngal / box_volume
    return theory_density_dict


def reset_hod(Ball, param_mapping) -> None:
    to_reset=['Acent','Asat','Bcent','Bsat']
    for tracer in param_mapping:
        for pname in to_reset:
            Ball.tracers[tracer][pname] = 0   

def get_enabled_tracers(HOD_params: dict) -> list:
    flags = HOD_params.get('tracer_flags', {}) or {}
    return [t for t, f in flags.items() if bool(f)] if isinstance(flags, dict) else []


def find_best_opt_sample(chain_prefix: str):

    pattern = f"{chain_prefix}_cmaes_opt_*.txt"
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No opt files found with pattern: {pattern}")

    best_params, best_file, best_nll = None, None, np.inf
    for fn in files:
        data = np.loadtxt(fn, ndmin=2)
        if data.ndim != 2 or data.shape[1] < 2:
            raise ValueError(f"Unexpected format in {fn}; need at least 2 columns (params + -loglike)")
        nll = -data[:, -1]
        i = int(np.argmin(nll))
        if nll[i] < best_nll:
            best_nll = float(nll[i])
            best_params = data[i, :-1].copy()
            best_file = fn
    if best_params is None:
        raise RuntimeError("Failed to select a best opt sample.")
    return best_params, best_file, best_nll


def extract_wp_xi(vec: np.ndarray):
    """Slice concatenated vector into (wp, xi0, xi2): 18/13/13 bins."""
    return vec[:18], vec[18:31], vec[31:44]


def save_clustering_ascii(out_root: str, tracer: str, chain_params: dict, sim_params: dict, clustering_real: dict, clustering_rsd: dict) -> None:
    z = float(sim_params.get('z_mock', 0.0))
    sim_name = sim_params.get('sim_name', 'SIM')

    tdir = ensure_dir(os.path.join(out_root, 'clustering', sim_name, tracer, f"z{z:.3f}"))

    rpbins = np.geomspace(0.01, 100.0, 25)
    rpbinsmid = 0.5 * (rpbins[1:] + rpbins[:-1])
    idxwp = np.arange(3, 21)   # 18 points
    idxxi = np.arange(8, 21)   # 13 points
    rp_wp = rpbinsmid[idxwp]
    s_xi = rpbinsmid[idxxi]

    key = f"{tracer}_{tracer}"
    if key not in clustering_real or key not in clustering_rsd:
        raise KeyError(f"Clustering key '{key}' not found in results.")

    wp_real, xi0_real, xi2_real = extract_wp_xi(clustering_real[key])
    wp_rsd,  xi0_rsd,  xi2_rsd  = extract_wp_xi(clustering_rsd[key])

    np.savetxt(os.path.join(tdir, chain_params.get('chain_prefix', None) + "_wp_real.dat"), np.column_stack((rp_wp, wp_real)))
    np.savetxt(os.path.join(tdir, chain_params.get('chain_prefix', None) + "_xi02_real.dat"), np.column_stack((s_xi, xi0_real, xi2_real)))

    np.savetxt(os.path.join(tdir, chain_params.get('chain_prefix', None) + "_wp_rsd.dat"), np.column_stack((rp_wp, wp_rsd)))
    np.savetxt(os.path.join(tdir, chain_params.get('chain_prefix', None) + "_xi02_rsd.dat"), np.column_stack((s_xi, xi0_rsd, xi2_rsd)))

