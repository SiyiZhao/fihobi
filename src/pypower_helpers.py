from pypower import CatalogFFTPower, mpi
import numpy as np

# To activate logging
# from pypower import setup_logging
# setup_logging()

## settings for pypower
mpicomm = mpi.COMM_WORLD
mpiroot = None # input positions/weights scattered on all processes
Lbox = 2000
Nmesh = 256
kmax = Nmesh*np.pi/Lbox
kedges = np.linspace(0, kmax, Nmesh//2+1)
edges = (kedges, np.linspace(-1., 1., 5))
ells=(0,2)

def apply_periodic(x, L):
        return (x + 0.5 * L) % L - 0.5 * L
def run_pypower(x, y, z, vz, rsd_fac, Lbox=Lbox, Nmesh=Nmesh, edges=edges, ells=ells, mpicomm=mpicomm, mpiroot=mpiroot):    
    ## positions
    pos = np.vstack((x, y, z)).T
    ## add RSD to z direction
    z_RSD=apply_periodic(pos[:, 2]+vz*rsd_fac, Lbox)
    pos[:, 2]=z_RSD
    weight = np.ones(len(pos))
    result = CatalogFFTPower(pos, data_weights1=weight, boxsize=Lbox, nmesh=Nmesh, 
                         resampler='tsc', interlacing=3, ells=ells, 
                         los='z', edges=edges,  position_type='pos', mpicomm=mpicomm, mpiroot=mpiroot)
    poles = result.poles
    return poles

def run_pypower_redshift(x, y, z, Lbox=Lbox, Nmesh=Nmesh, edges=edges, ells=ells, mpicomm=mpicomm, mpiroot=mpiroot):    
    ## positions
    pos = np.vstack((x, y, z)).T
    weight = np.ones(len(pos))
    result = CatalogFFTPower(pos, data_weights1=weight, boxsize=Lbox, nmesh=Nmesh, 
                         resampler='tsc', interlacing=3, ells=ells, 
                         los='z', edges=edges,  position_type='pos', mpicomm=mpicomm, mpiroot=mpiroot)
    poles = result.poles
    return poles