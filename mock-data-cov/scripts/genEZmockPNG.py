# !/usr/bin/env python3
# the workdir is ~/projects/fihobi/mock-data-cov/
# need nthread=16 for EZmock

import sys
import os, subprocess
import numpy as np
from EZmock import EZmock
current_dir = os.getcwd()
source_dir = os.path.join(current_dir, "source")
if source_dir not in sys.path:
    sys.path.insert(0, source_dir)
from config_helpers import generate_2lpt_param
# from pypower_helpers import run_pypower
from pypower_helpers import run_pypower_redshift


seed = sys.argv[1] 
odir='/pscratch/sd/s/siyizhao/EZmock/output/mocks/QSO-z4_c300'
redshift = 2.0
fnl = 470.
ntracer = 3288003
rho_c, rho_exp, pdf_base, sigma_v = [0.89981, 4.4848, 0.4031527, 468.7988]

pdir='/pscratch/sd/s/siyizhao/2LPTdisp/'
Omega_m0 = 0.315192
z_pk = 1
Lbox = 2000
Ngrid = 256
EZseed = 42
nthread=16
ells = (0, 2)

# prepare parameter file for 2LPTnonlocal --------------------------------------

generate_2lpt_param(seed=seed, redshift=redshift, fnl=fnl, output_path=f'configs/params_2lpt/r{seed}.param')
print(f"Generated configs/params_2lpt/r{seed}.param")

# prepare displacement field with 2LPTnonlocal ---------------------------------
print(f'Generating 2LPT displacement field for seed {seed}...')

home = os.path.expanduser("~")
cmd = [
    f"{home}/lib/2LPTic_PNG/2LPTnonlocal",
    f"configs/params_2lpt/r{seed}.param"
]
# Ensure LD_LIBRARY_PATH is exported in the Python process so child processes
#+ and any dynamic loader used by Python can find the FFTW/shared libs.
new_ld = f"{home}/lib/fftw-2.1.5/lib:{home}/.conda/envs/ezmock_png/lib" # fftw2 and gsl paths
if os.environ.get("LD_LIBRARY_PATH"):
    new_ld = new_ld + ":" + os.environ.get("LD_LIBRARY_PATH")
os.environ["LD_LIBRARY_PATH"] = new_ld

# Use a snapshot of os.environ for subprocess.run and ensure single-threaded
env = os.environ.copy()
env.setdefault("OMP_NUM_THREADS", "1")

# create logs directory in the current working directory
logs_dir = os.path.abspath(os.path.join(os.getcwd(), 'logs'))
os.makedirs(logs_dir, exist_ok=True)
logpath = os.path.join(logs_dir, f"2lpt_{seed}.log")
with open(logpath, "w") as logfile:
    try:
        subprocess.run(cmd, env=env, stdout=logfile, stderr=subprocess.STDOUT, check=True)
    except subprocess.CalledProcessError as e:
        print(f"2LPT failed for seed {seed}, returncode {e.returncode}. See {logpath}")
        raise
    
print('Done.')


# generate EZmock and save -----------------------------------------------------
# ensure the Python process (and libraries) use the desired thread count for EZmock
ez = EZmock(Lbox=Lbox, Ngrid=Ngrid, seed=EZseed, nthread=nthread)
ez.eval_growth_params(z_out=redshift, z_pk=z_pk, Omega_m=Omega_m0)
mydx = np.loadtxt(pdir + f'dispx_{seed}.txt')
mydy = np.loadtxt(pdir + f'dispy_{seed}.txt')
mydz = np.loadtxt(pdir + f'dispz_{seed}.txt')
ez.create_dens_field_from_disp(mydx, mydy, mydz, deepcopy=True)
rsd_fac = (1 + redshift) / (100 * np.sqrt(Omega_m0 * (1 + redshift)**3 + (1 - Omega_m0)))
# x, y, z, vx, vy, vz = ez.populate_tracer(rho_c, rho_exp, pdf_base, sigma_v, ntracer)
filename= odir + f'/EZmock_r{seed}.txt'
ez.populate_tracer_to_file(rho_c, rho_exp, pdf_base, sigma_v, ntracer, filename, rsd_fac=rsd_fac)

print('EZmock generated and saved to', filename)


# measure pypower poles and save------------------------------------------------
data = np.loadtxt(filename)
x = data[:, 0]
y = data[:, 1]
z_rsd = data[:, 2]
poles = run_pypower_redshift(x, y, z_rsd, ells=ells)
outpath = odir + f'/pypowerpoles_r{seed}.npy'
poles.save(outpath)
print(f"Saved pypower poles to {outpath}")
# poles = run_pypower(x, y, z, vz, rsd_fac)
# poles_all.append(poles)

print(f'Finished seed {seed}.')
