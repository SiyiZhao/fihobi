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
    'write_catalogs',
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


def write_catalogs(Ball, mock_real: dict, fit_params: dict, out_root=None, custom_prefix=None) -> None:


    def z_to_tag(z):
        return f"{float(z):.3f}".replace('.', 'p')

    # Pull meta directly from Ball
    sim_name = getattr(Ball, 'sim_name', None) or Ball.params.get('sim_name')
    if sim_name is None:
        raise KeyError("Ball.sim_name (or Ball.params['sim_name']) is required.")
    zsnap = float(Ball.params.get('z', 0.0))
    redshift_tag = z_to_tag(zsnap)

    boxsize = float(Ball.params.get('Lbox'))
    velz2kms = float(Ball.params.get('velz2kms'))

    # Constants for pathing
    mock_type = 'abacus_HF'
    version = 'DR2_v2.0'

    base_dir = os.path.join(out_root, mock_type, version, sim_name, 'Boxes')
    ensure_dir(base_dir)

    for tracer, cat in mock_real.items():
        tracer_dir = ensure_dir(os.path.join(base_dir, tracer))

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
        if custom_prefix is None:
            fname = f"{mock_type}_{tracer}_{redshift_tag}_{version}_{sim_name}_clustering.dat.h5"
        else:
            fname = f"{mock_type}_{tracer}_{redshift_tag}_{version}_{sim_name}_{custom_prefix}_clustering.dat.h5"
        outpath = os.path.join(tracer_dir, fname)

        Catalog(data=data).write(outpath, header=hdr)
        print(f"[write] {tracer} -> {outpath}")
