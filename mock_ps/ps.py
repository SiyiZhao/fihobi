#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a script for measuring power spectrum of mock catalog.

Usage
-----
$ python ./ps.py --help
"""
import argparse
import numpy as np

from pypower import CatalogFFTPower, mpi

# To activate logging
# from pypower import setup_logging
# setup_logging()

mpicomm = mpi.COMM_WORLD
mpiroot = None # input positions/weights scattered on all processes

def parse_args():
    parser = argparse.ArgumentParser(description='Measure power spectrum of mock catalog')
    parser.add_argument('data_file', help='Input data file (ASCII format)')
    parser.add_argument('--skiprows', type=int, default=15, help='Number of header rows to skip in the data file. Default is 15 for AbacusHOD output.')
    parser.add_argument('--boxsize', type=float, default=2000., help='Box size in Mpc/h')
    parser.add_argument('--redshift', type=float, default=0., help='Redshift of the catalog')
    parser.add_argument('--add_RSD', type=bool, default=False, help='Whether to add RSD to z direction, if you use catalog without RSD and want to add RSD to power spectrum, set True. Notice that RSD has already been added to z-axis in AbacusHOD if `want_rsd: True`, the dir name would contain "_rsd".')
    parser.add_argument('--nmesh', type=int, default=128, help='Number of mesh cells per dimension')
    parser.add_argument('--kmin', type=float, default=0., help='Minimum k value, default is 0')
    parser.add_argument('--kmax', type=float, default=None, help='Maximum k value, default is None, which sets kmax to the Nyquist mode kNy=nmesh*pi/boxL')
    parser.add_argument('--nkbins', type=int, default=None, help='Number of k bins, default is None, which sets nkbins to nmesh/2')
    parser.add_argument('--mubins', type=int, default=4, help='Number of mu bins for 2D power spectrum, default is 4, which gives mu edges [-1,-0.5,0,0.5,1]')
    parser.add_argument('--output', default='power.npy', help='Output file path for power spectrum')
    parser.add_argument('--plot', default=None, help='Output plot path', required=False)
    return parser.parse_args()

### settings
args = parse_args()
data_fn = args.data_file
fn = args.output
boxL = args.boxsize
z = args.redshift
add_RSD = args.add_RSD
Nmesh = args.nmesh
kmin, kmax, nkbins = args.kmin, args.kmax, args.nkbins
if kmax is None:
    kmax = Nmesh*np.pi/boxL
if nkbins is None:
    nkbins = Nmesh//2
kedges = np.linspace(kmin, kmax, nkbins+1)
ells = (0, 2, 4)
mubins = args.mubins
edges = (kedges, np.linspace(-1., 1., mubins+1))
plot_path = args.plot if hasattr(args, 'plot') and args.plot else None

if add_RSD==True:
    ### cosmology for RSD
    Om0 = 0.315192
    Ode0 = 0.684808
    VELZ2KMS = 100 * np.sqrt(Om0 * (1+z)**3 + Ode0 ) / (1+z)
    def apply_periodic(x, L):
        return (x + 0.5 * L) % L - 0.5 * L

def read(filename, weight=None):
    data = np.loadtxt(filename, skiprows=args.skiprows)
    pos = data[:, :3]
    if add_RSD==True:
        ## add RSD to z direction
        z_RSD=apply_periodic(pos[:, 2]+data[:, 5]/VELZ2KMS, boxL)
        pos[:, 2]=z_RSD
    if weight is None:
        weight = np.ones(len(data))
    return pos, weight

data_positions, data_weights = read(data_fn)


# pass mpiroot=0 if input positions and weights are not MPI-scattered
result = CatalogFFTPower(data_positions, data_weights1=data_weights, boxsize=boxL, nmesh=Nmesh, 
                         resampler='tsc', interlacing=3, ells=ells, 
                         los='z', edges=edges,  position_type='pos', mpicomm=mpicomm, mpiroot=mpiroot)
# wavenumber array in result.poles.k
# multipoles in result.poles.power


poles = result.poles
print('Shot noise is {:.4f}.'.format(poles.shotnoise)) # cross-correlation, shot noise is 0.
print('Normalization is {:.4f}.'.format(poles.wnorm))

## save
result.save(fn)

## plot
if plot_path is not None:
    from matplotlib import pyplot as plt
    import matplotlib as mpl
    mpl.rc_file('../fig/matplotlibrc')

    ax = plt.gca()
    for ill, ell in enumerate(poles.ells):
        # Calling poles() removes shotnoise for ell == 0 by default;
        # Pass remove_shotnoise = False if you do not want to;
        # See get_power() for all arguments
        ax.plot(*poles(ell=ell, return_k=True, complex=False), label=r'$\ell = {:d}$'.format(ell))
    ax.set_xlabel(r'$k$ [$h/\mathrm{Mpc}$]')
    ax.set_ylabel(r'$P_l(k)$ [$(\mathrm{Mpc}/h)^{3}$]')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
