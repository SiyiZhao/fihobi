# Credit: https://github.com/ahnyu/hod-variation/blob/main/source/loading_helpers.py , modified for our use case


from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union, List

import yaml


# ---------- Default configuration (edit as needed) ----------
DEFAULT_CONFIG: Dict[str, Any] = {
    "HOD_params": {
        "LRG_params": {
            "alpha": 1.02,
            "alpha_c": 0.2,
            "alpha_s": 0.99,
            "ic": 1.0,
            "kappa": 1.27,
            "logM1": 13.81,
            "logM_cut": 12.67,
            "sigma": 0.02,
            "profile_code": 1,
        },
        "tracer_flags": {"ELG": False, "LRG": True, "QSO": False},
        "use_particles": False,
        "use_profiles": True,
        "want_dv": False,
        "want_AB": True,
        "want_rsd": True,
        "write_to_disk": False,
    },
    "chain_params": {
        "chain_prefix": "LRG_z0_all",
        "output_dir": "/pscratch/sd/h/hanyuz/desi-dr2-hod/LRG/z0/",
    },
    "clustering_params": {
        "bin_params": {"logmax": 1.5, "logmin": -1.5, "nbins": 18},
        "clustering_type": "all",
        "pi_bin_size": 40,
        "pimax": 40,
    },
    "data_params": {
        "tracer_combos": {
            "LRG_LRG": {
                "path2cov": "/global/cfs/cdirs/desi/users/hanyuz/projects/desi-dr2-hod/data4fit/cov_LRG_0.4_0.6_cut.dat",
                "path2wp": "/global/cfs/cdirs/desi/users/hanyuz/projects/desi-dr2-hod/data4fit/wp_LRG_0.4_0.6_cut.dat",
                "path2xi02": "/global/cfs/cdirs/desi/users/hanyuz/projects/desi-dr2-hod/data4fit/xi02_LRG_0.4_0.6_cut.dat",
            }
        },
        "tracer_density_mean": {"LRG": 5.28198e-04},
        "tracer_density_std": {"LRG": 5.28198e-05},
    },
    "fit_params": {
        "LRG": {
            "alpha": [3, 0, 2],
            "kappa": [4, 0, 10],
            "logM1": [1, 12.5, 15.5],
            "logM_cut": [0, 12, 13.8],
            "sigma": [2, 0.001, 3],
        }
    },
    "nthread": 64,
    "prepare_sim": {"Nparallel_load": 18},
    "sim_params": {
        "cleaned_halos": True,
        "output_dir": "/pscratch/sd/h/hanyuz/desi-dr2-hod/mocks/",
        "sim_dir": "/global/cfs/projectdirs/desi/cosmosim/Abacus/",
        "sim_name": "AbacusSummit_base_c000_ph000",
        "subsample_dir": "/pscratch/sd/h/hanyuz/AbacusSummit/subsample_desidr2_profile_withAB/",
        "z_mock": 0.5,
        "force_mt": True,
    },
    "cma_options": {"popsize": 100, "maxiter": 200},
}


# ---------- Internals ----------
def _deep_update(base: Dict[str, Any], updates: Mapping[str, Any]) -> Dict[str, Any]:
    """Recursively merge 'updates' into 'base'. Adds new dicts/keys as needed."""
    for k, v in updates.items():
        if isinstance(v, Mapping) and isinstance(base.get(k), Mapping):
            _deep_update(base[k], v)  # type: ignore[index]
        else:
            base[k] = v
    return base


def _set_by_dotted_key(d: Dict[str, Any], dotted_key: str, value: Any) -> None:
    """Set d['a']['b']['c'] when dotted_key='a.b.c', creating dicts as needed."""
    parts = dotted_key.split(".")
    cur: Dict[str, Any] = d
    for p in parts[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[p] = nxt
        cur = nxt  # type: ignore[assignment]
    cur[parts[-1]] = value


def _del_by_dotted_key(d: Dict[str, Any], dotted_key: str, *, strict: bool = False) -> None:
    """
    Delete key at dotted path. If strict=True, raises KeyError when path/key missing.
    Otherwise it's a no-op when missing.
    """
    parts = dotted_key.split(".")
    cur: Dict[str, Any] = d
    for p in parts[:-1]:
        nxt = cur.get(p, None)
        if not isinstance(nxt, dict):
            if strict:
                raise KeyError(f"Path not found at '{p}' in '{dotted_key}'")
            return
        cur = nxt  # type: ignore[assignment]
    key = parts[-1]
    if key in cur:
        cur.pop(key, None)
    elif strict:
        raise KeyError(f"Key '{key}' not found in '{dotted_key}'")


def _apply_overrides(base: Dict[str, Any], overrides: Mapping[str, Any]) -> Dict[str, Any]:
    """Apply nested dict overrides or dotted-key overrides (or both)."""
    base = deepcopy(base)
    for k, v in overrides.items():
        if "." in k:
            _set_by_dotted_key(base, k, v)
        elif isinstance(v, Mapping):
            base.setdefault(k, {})
            if not isinstance(base[k], Mapping):
                base[k] = {}
            _deep_update(base[k], v)  # type: ignore[index]
        else:
            base[k] = v
    return base


def _prune_empty_dicts(obj: Any) -> Any:
    """Recursively remove empty dicts after deletions (tidies the output)."""
    if isinstance(obj, dict):
        pruned = {k: _prune_empty_dicts(v) for k, v in obj.items()}
        return {k: v for k, v in pruned.items() if not (isinstance(v, dict) and not v)}
    if isinstance(obj, list):
        return [_prune_empty_dicts(x) for x in obj]
    return obj


# ---------- Public API ----------
def generate_config(
    overrides: Optional[Mapping[str, Any]] = None,
    *,
    remove: Optional[Union[str, Iterable[str]]] = None,
    template_path: Optional[str] = None,
    output_path: Optional[str] = None,
    strict_remove: bool = False,
    prune_empty: bool = True,
) -> str:
    """
    Build a YAML config (optionally from a template), apply overrides, optionally remove keys,
    and return YAML text. Writes to 'output_path' if provided.

    Parameters
    ----------
    overrides : dict
        Nested dicts and/or dotted keys. Adds/overrides values and can create new sections.
    remove : iterable of str or single str
        Dotted paths to delete (e.g., "data_params.tracer_combos.LRG_LRG.path2xi02").
    template_path : str
        Load starting config from YAML file instead of DEFAULT_CONFIG.
    strict_remove : bool
        If True, raise KeyError when a remove path doesn't exist.
    prune_empty : bool
        If True, drop any dicts that become empty after removals.
    """
    # 1) Base
    if template_path:
        with open(template_path, "r", encoding="utf-8") as f:
            base = yaml.safe_load(f) or {}
    else:
        base = deepcopy(DEFAULT_CONFIG)

    # 2) Overrides (adds/changes keys)
    if overrides:
        base = _apply_overrides(base, overrides)

    # 3) Removals
    if remove:
        if isinstance(remove, str):
            remove = [remove]
        for path in remove:
            _del_by_dotted_key(base, path, strict=strict_remove)

    # 4) Optional prune of emptied dicts
    if prune_empty:
        base = _prune_empty_dicts(base)

    # 5) Dump
    text = yaml.safe_dump(base, sort_keys=False, default_flow_style=False, allow_unicode=True)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    return text


def fit_params_overrides(
    spec_by_tracer: Mapping[str, Mapping[str, Iterable[float]]],
    *,
    tracer_order: Tuple[str, ...] = ("LRG", "ELG", "QSO"),
) -> Dict[str, Any]:
    """
    Build an overrides dict for 'fit_params' with global indices beginning at 0.

    Parameters
    ----------
    spec_by_tracer : dict
        {
          "LRG": {"names": ["alpha", "kappa"], "lo": [0, 0], "hi": [2, 10]},
          "ELG": {"names": ["alpha"], "lo": [0], "hi": [2]},
          ...
        }
        Lists must match in length for each tracer.
    tracer_order : tuple
        Global assignment order; controls the index sequence.

    Returns
    -------
    overrides : dict
        {"fit_params": {"LRG": {"alpha": [0, 0.0, 2.0], ...}, "ELG": {...}, ...}}
    """
    idx = 0
    out: Dict[str, Dict[str, List[float]]] = {}

    for tracer in tracer_order:
        if tracer not in spec_by_tracer:
            continue
        entry = spec_by_tracer[tracer]
        names = list(entry.get("names", []))
        lo = list(entry.get("lo", []))
        hi = list(entry.get("hi", []))

        if not (len(names) == len(lo) == len(hi)):
            raise ValueError(
                f"{tracer}: 'names', 'lo', and 'hi' must have equal length "
                f"(got {len(names)}, {len(lo)}, {len(hi)})."
            )
        # guard duplicates within a tracer
        if len(set(names)) != len(names):
            dupes = sorted({n for n in names if names.count(n) > 1})
            raise ValueError(f"{tracer}: duplicate parameter names: {dupes}")

        tdict: Dict[str, List[float]] = out.setdefault(tracer, {})
        for n, l, h in zip(names, lo, hi):
            l = float(l)
            h = float(h)
            if l > h:
                raise ValueError(f"{tracer}.{n}: lower bound {l} > upper bound {h}.")
            tdict[n] = [idx, l, h]
            idx += 1

    return {"fit_params": out}


def merge_overrides(*parts: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Combine multiple override dicts into one. Later parts take precedence.
    Dotted keys are kept as-is for generate_config to interpret.
    """
    out: Dict[str, Any] = {}
    for p in parts:
        for k, v in p.items():
            if "." in k:
                # Treat dotted keys atomically
                out[k] = v
            elif isinstance(v, Mapping) and isinstance(out.get(k), dict):
                # deep merge
                _deep_update(out[k], v)  # type: ignore[index]
            else:
                out[k] = deepcopy(v) if isinstance(v, Mapping) else v
    return out

def generate_slurm_launcher(
    time_hms: str,
    config_path: str,
    chain_path: str,
    *,
    job_name: str | None = None,
    logs_dir: str | None = None,   # defaults to workdir/logs if None
    account: str = "desi",
    qos: str = "regular",
    ntasks: int = 4,
    cpus_per_task: int = 64,
    constraint: str = "cpu",
    omp_num_threads: int = 64,
    conda_env: str = "hod_variation",
    workdir: str = "/global/homes/s/siyizhao/projects/fihobi/hod-variation",
    entry: str = "scripts/run_pmn.py",
    output_path: str | None = None,
    make_executable: bool = True,
) -> str:
    """
    Build a Slurm launcher script (as text) and optionally write it to `output_path`.
    `logs_dir` defaults to f"{workdir}/logs".
    """
    if job_name is None:
        job_name = Path(config_path).stem
    if logs_dir is None:
        logs_dir = str(Path(workdir) / "logs")

    script = f"""#!/bin/bash

#SBATCH --job-name={job_name}
#SBATCH --output={logs_dir}/%x_%j.log
#SBATCH --error={logs_dir}/%x_%j.err
#SBATCH --qos={qos}
#SBATCH --account={account}
#SBATCH --time={time_hms}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH -C {constraint}

source /global/common/software/desi/desi_environment.sh

export PYTHONPATH=$PYTHONPATH:$HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/lib/MultiNest/lib
export OMP_NUM_THREADS={omp_num_threads}
outdir={chain_path}
mkdir -p $outdir
config={config_path}
cd {workdir}

srun -n 4 -c 64 python -m abacusnbody.hod.prepare_sim_profiles --path2config $config
srun -n {ntasks} -c {cpus_per_task} python {entry} --config $config > $outdir/run.log 2>&1
srun -n 1 -c 64 python scripts/post.py --config $config > $outdir/post.log 2>&1
""".lstrip()

    if output_path:
        outp = Path(output_path)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(script, encoding="utf-8")
        if make_executable:
            outp.chmod(outp.stat().st_mode | 0o111)

    return script


__all__ = [
    "DEFAULT_CONFIG",
    "generate_config",
    "fit_params_overrides",
    "merge_overrides",
    "generate_slurm_launcher",
]