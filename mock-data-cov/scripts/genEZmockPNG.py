# !/usr/bin/env python3
# the workdir is ~/projects/fihobi/mock-data-cov/
# need nthread=16 for EZmock

import yaml
import os, sys
import numpy as np
from EZmock import EZmock
current_dir = os.getcwd()
source_dir = os.path.join(current_dir, "source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from disp2LPT_helper import run_disp_2lpt
sys.path.insert(0, os.path.expanduser('../src'))
from pypower_helpers import run_pypower
# from pypower_helpers import run_pypower_redshift


seed = sys.argv[1] 
odir = sys.argv[2]
config = yaml.safe_load(open(sys.argv[3]))
# odir=config['odir']
redshift = config['redshift']
fnl = config['fnl4ezmocks']
ntracer = config['ntracer']
rho_c, rho_exp, pdf_base, sigma_v = [config['rho_c'], config['rho_exp'], config['pdf_base'], config['sigma_v']]

pdir='/pscratch/sd/s/siyizhao/2LPTdisp/'
Omega_m0 = 0.3137721
Omega_nu = 0.00141976532
z_pk = 1
Lbox = 2000
Ngrid = 512 
EZseed = 42
nthread=os.environ.get('OMP_NUM_THREADS', 16)
ells = (0)

# prepare displacement field with 2LPTnonlocal ---------------------------------
run_disp_2lpt(seed=seed, redshift=redshift, fnl=fnl, Ngrid=Ngrid, Lbox=Lbox, fix_amp=0) # no fixed amplitude for generating EZmock



# generate EZmock and save -----------------------------------------------------
# ensure the Python process (and libraries) use the desired thread count for EZmock
print(f"Generating EZmock for seed {seed}...")
print(f"nthread={nthread}")
ez = EZmock(Lbox=Lbox, Ngrid=Ngrid, seed=EZseed, nthread=nthread)
ez.eval_growth_params(z_out=redshift, z_pk=z_pk, Omega_m=Omega_m0, Omega_nu=Omega_nu)
mydx = np.loadtxt(pdir + f'dispx_{seed}.txt')
mydy = np.loadtxt(pdir + f'dispy_{seed}.txt')
mydz = np.loadtxt(pdir + f'dispz_{seed}.txt')
ez.create_dens_field_from_disp(mydx, mydy, mydz, deepcopy=True)
print("Displacement field loaded.")
rsd_fac = (1 + redshift) / (100 * np.sqrt(Omega_m0 * (1 + redshift)**3 + (1 - Omega_m0)))
x, y, z, vx, vy, vz = ez.populate_tracer(rho_c, rho_exp, pdf_base, sigma_v, ntracer)
print('EZmock generated, now measuring pypower poles...')
# filename= odir + f'/EZmock_r{seed}.txt'
# ez.populate_tracer_to_file(rho_c, rho_exp, pdf_base, sigma_v, ntracer, filename, rsd_fac=rsd_fac)
# print('EZmock generated and saved to', filename)


# measure pypower poles and save------------------------------------------------
# data = np.loadtxt(filename)
# x = data[:, 0]
# y = data[:, 1]
# z_rsd = data[:, 2]
# poles = run_pypower_redshift(x, y, z_rsd, ells=ells)
poles = run_pypower(x, y, z, vz, rsd_fac, ells=ells)
outpath = odir + f'/pypowerpoles_r{seed}.npy'
poles.save(outpath)
print(f"Saved pypower poles to {outpath}")
# poles_all.append(poles)

print(f'Finished seed {seed}.')
