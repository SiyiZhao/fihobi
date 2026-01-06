#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightcone.prep_nz -- prepare n(z) file for cutsky.
"""
import numpy as np

__all__ = [
    "prep_nz_file",
]

def prep_nz_file(in_path, out_path):
    """Prepare the n(z) file for cutsky generation.

    Args:
        in_path (str): Path to the input n(z) file.
        out_path (str): Path to save the output n(z) file.
    """
    data = np.loadtxt(in_path)
    # zmid zlow zhigh n(z) Nbin Vol_bin
    zmid = data[:, 0]
    nz = data[:, 3]
    zlow = data[:, 1]
    zhigh = data[:, 2]
    data_2 = np.column_stack((zmid, nz))
    data_out = np.row_stack(([zlow[0], nz[0]], data_2, [zhigh[-1], nz[-1]]))

    np.savetxt(out_path, data_out, header=f'original file {in_path}\n zmid n(z)')
    print(f"[write] n(z) file -> {out_path}")

if __name__ == "__main__":
    ## LRG NGC
    in_path = '/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/LRG_NGC_nz.txt'
    out_path = '/global/homes/s/siyizhao/projects/fihobi/data/nz/LRG_NGC_nz_v2.txt'
    prep_nz_file(in_path, out_path)
        
    ## LRG SGC
    in_path = '/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/LRG_SGC_nz.txt'
    out_path = '/global/homes/s/siyizhao/projects/fihobi/data/nz/LRG_SGC_nz_v2.txt'
    prep_nz_file(in_path, out_path)

    ## QSO NGC
    in_path = '/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/QSO_NGC_nz.txt'
    out_path = '/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_NGC_nz_v2.txt'
    prep_nz_file(in_path, out_path)

    ## QSO SGC
    in_path = '/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/QSO_SGC_nz.txt'
    out_path = '/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_SGC_nz_v2.txt'
    prep_nz_file(in_path, out_path)
    