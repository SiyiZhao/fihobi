#!/usr/bin/env python3
"""
pkEZmock.py

Scan directories matching:
    /pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300/EZmock_*
For each directory, find a file containing at least three columns (x, y, z_rsd),
call run_pypower_redshift from source/pypower_helpers.py and save the poles to
/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300/pypowerpoles_*.npz
"""
import numpy as np
from pathlib import Path
import os, sys
sys.path.insert(0, os.path.expanduser('../src'))
from pypower_helpers import run_pypower_redshift


IN_PATTERN = Path("/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300")
OUT_DIR = IN_PATTERN  # save outputs alongside
glob_pattern = IN_PATTERN / "EZmock_*"
# ells = (0)
ells = (0, 2)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    matches = list(glob_pattern.parent.glob(glob_pattern.name))
    if not matches:
        print(f"No paths match pattern {glob_pattern}")
        return

    for p in matches:
        arr = None
        input_path = None

        if p.is_file():
            input_path = p
            try:
                arr = np.loadtxt(input_path)
            except Exception as e:
                print(f"Failed to load file {input_path}: {e}")
                continue
        elif p.is_dir():
            # find first file inside the directory with >=3 columns
            for f in p.iterdir():
                if not f.is_file():
                    continue
                try:
                    candidate = np.loadtxt(f)
                except Exception:
                    continue
                if candidate.ndim == 1 and candidate.size >= 3:
                    arr = candidate
                    input_path = f
                    break
                if candidate.ndim == 2 and candidate.shape[1] >= 3:
                    arr = candidate
                    input_path = f
                    break
            if input_path is None:
                print(f"No suitable file with >=3 columns found in directory {p}")
                continue
        else:
            # skip non-file, non-dir matches
            continue

        # Ensure we have data with at least three columns
        if arr is None:
            print(f"No data loaded for {p}")
            continue

        if arr.ndim == 1:
            if arr.size < 3:
                print(f"Loaded 1D array with <3 values from {input_path}")
                continue
            x = np.atleast_1d(arr[0])
            y = np.atleast_1d(arr[1])
            z_rsd = np.atleast_1d(arr[2])
        else:
            if arr.shape[1] < 3:
                print(f"Loaded array with <3 columns from {input_path}")
                continue
            x = arr[:, 0]
            y = arr[:, 1]
            z_rsd = arr[:, 2]

        try:
            poles = run_pypower_redshift(x, y, z_rsd, ells=ells)
        except Exception as e:
            print(f"run_pypower_redshift failed for {input_path}: {e}")
            continue

        # construct output filename by replacing "EZmock" with "pypowerpoles"
        out_name = input_path.name.replace("EZmock", "pypowerpoles")
        if out_name.endswith(".txt"):
            out_name = out_name[:-4] + ".npz"
        elif not out_name.endswith(".npz"):
            out_name = out_name + ".npz"
        out_path = Path(OUT_DIR) / out_name

        try:
            if isinstance(poles, dict):
                np.savez(out_path, **poles)
            else:
                np.savez(out_path, poles=poles)
            print(f"Saved pypower poles to {out_path}")
        except Exception as e:
            print(f"Failed to save poles to {out_path}: {e}")

if __name__ == "__main__":
    main()
        