#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
lightcone.prep_cutsky -- prepare cutsky configuration file and the input catalog in the required format.

Usage
-----
$ source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for mockfactory
$ python prep_cutsky.py

Author: Siyi Zhao
"""
from pathlib import Path
import numpy as np
from mockfactory import Catalog

__all__ = [
    "prep_cat_in_ASCII_format",
    "write_cutsky_cfg",
]

def prep_cat_in_ASCII_format(
    input_path: str,
    output_path: str,
    boxsize: float | None = None,
) -> None:
    """Prepare the input catalog in ASCII format required by cutsky.

    Args:
        input_path (str): Path to the input catalog file.
        output_path (str): Path to save the formatted ASCII catalog.
        boxsize (float | None, optional): Size of the simulation box in Mpc/h. If provided, apply periodic wrapping. Defaults to None.
    """
    cat=Catalog.read(input_path)
    x = cat['X']
    y = cat['Y']
    z = cat['Z']
    vx = cat['VX']
    vy = cat['VY']
    vz = cat['VZ']
    # If boxsize is provided, apply periodic wrapping
    if boxsize is not None:
        x = x % boxsize
        y = y % boxsize
        z = z % boxsize
    # Prepare the output in the required format
    formatted_data = np.column_stack((x, y, z, vx, vy, vz))
    header = "X Y Z VX VY VZ"
    np.savetxt(output_path, formatted_data, header=header, comments='#', fmt='%.6f')
    print(f"[write] Formatted catalog -> {output_path}")

def write_cutsky_cfg(
    box_path: str,
    boxsize: float,
    lc_out_path: str,
    Omega_m: float = 0.315192,
    Omega_l: float | None = None,
    w_DE_EOS: float = -1.0,
    footprint_path: str = '/global/homes/s/siyizhao/lib/cutsky/scripts/Y3_dark_circle.dat_final_res7.ply',
    galactic_cap: str = 'N',
    nz_path: str = '/global/cfs/cdirs/desi/survey/catalogs/DA2/LSS/loa-v1/LSScats/v2/PIP/LRG_NGC_nz.txt',
    zmin: float = 0.405,
    zmax: float = 0.6,
    write_to: str | None = None,
    make_executable: bool = False,
) -> str:
    """Write the cutsky configuration file.

    Args:
        box_path (str): Path to the input catalog.
        boxsize (float): Size of the simulation box in Mpc/h.
        lc_out_path (str): Path to save the output lightcone catalog.
        Omega_m (float, optional): Matter density parameter. Defaults to 0.315192 ('DESI' value).
        Omega_l (float, optional): Dark energy density parameter. If None, it is set to 1 - Omega_m. Defaults to None.
        w_DE_EOS (float, optional): Dark energy equation of state parameter. Defaults to -1.0.
        footprint_path (str, optional): Path to the footprint file. Defaults to '/global/homes/s/siyizhao/lib/cutsky/scripts/Y3_dark_circle.dat_final_res7.ply'.
        galactic_cap (str, optional): Galactic cap to use ('N' or 'S'). Defaults to 'N'.
        nz_path (str, optional but recommended): Path to the n(z) file. 
        zmin (float, optional but recommended): Minimum redshift. Defaults to 0.405.
        zmax (float, optional but recommended): Maximum redshift. Defaults to 0.6.
        write_to (str | None, optional): If provided, write the configuration to this path. Defaults to None.
        make_executable (bool, optional): If True and write_to is provided, make the output file executable. Defaults to False.
    """
    if Omega_l is None:
        Omega_l = 1 - Omega_m
    conf_content = f"""# Configuration file for cutsky (default: `cutsky.conf').
INPUT          = '{box_path}'
INPUT_FORMAT  = 0
COMMENT        = '#'
BOX_SIZE       = {boxsize}
OMEGA_M        = {Omega_m}
OMEGA_LAMBDA   = {Omega_l}
DE_EOS_W       = {w_DE_EOS}
FOOTPRINT_TRIM = '{footprint_path}'
GALACTIC_CAP   = ['{galactic_cap}']
NZ_FILE        = '{nz_path}'
ZMIN           = {zmin}
ZMAX           = {zmax}
RAND_SEED      = [42]
OUTPUT         = ['{lc_out_path}']
"""
    if write_to:
        outp = Path(write_to)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(conf_content, encoding="utf-8")
        print(f"[write] -> {write_to}")
        if make_executable:
            outp.chmod(outp.stat().st_mode | 0o111)
            print(f"[chmod +x] -> {write_to}")
    return conf_content

if __name__ == "__main__":
    import os
    catalog_path = '/pscratch/sd/s/siyizhao/desi-dr2-hod/mocks_base-A_v2/abacus_HF/DR2_v2.0/Abacus_pngbase_c302_ph000/Boxes/QSO/z3p000/abacus_HF_QSO_3p000_DR2_v2.0_Abacus_pngbase_c302_ph000_MAP_realspace_clustering.dat.h5'
    boxsize = 2000.0  # Mpc/h
    WORKDIR = 'works/test_prep_cutsky'
    os.makedirs(WORKDIR, exist_ok=True)
    galactic_cap = 'N'  # 'N' or 'S'
    nz_path = '/global/homes/s/siyizhao/projects/fihobi/data/nz/QSO_NGC_nz_v2.txt'
    zmin = 2.8
    zmax = 3.5
    box_path = WORKDIR + f'/box_{galactic_cap}_{zmin}_{zmax}.dat'
    lc_path = WORKDIR + f'/cutsky_{galactic_cap}_{zmin}_{zmax}.dat'
    write_to = WORKDIR + f'/cutsky_{galactic_cap}_{zmin}_{zmax}.conf'

    prep_cat_in_ASCII_format(
        input_path=catalog_path,
        output_path=box_path,
        boxsize=boxsize,
    )
    
    write_cutsky_cfg(
        box_path=box_path,
        boxsize=boxsize,
        lc_out_path=lc_path,
        galactic_cap=galactic_cap,
        nz_path=nz_path,
        zmin=zmin,
        zmax=zmax,
        write_to=write_to,
    )
    
    print(f"Done preparing cutsky configuration and input catalog. Just run:")
    print(f"/global/homes/s/siyizhao/lib/cutsky/CUTSKY -c {write_to} > {WORKDIR}/lc_test.log 2>&1")
    