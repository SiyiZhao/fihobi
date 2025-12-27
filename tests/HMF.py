import sys, os
import numpy as np
from matplotlib import pyplot as plt
sys.path.insert(0, os.path.expanduser('~/lib/'))
import abacusnbody
print(abacusnbody.__file__)
from abacusnbody.data.compaso_halo_catalog import CompaSOHaloCatalog
import abacusnbody.metadata


def read_particle_mass():
    meta = abacusnbody.metadata.get_meta('AbacusSummit_base_c000_ph000', redshift=3)
    m_p = meta['ParticleMassHMsun'] # Particle mass in h^-1 Msun
    print(f'Particle mass in AbacusSummit: {m_p:.3e} h^-1 Msun')
    m_p *= 6912**3/4096**3 # pngbase has lower resolution
    print(f'Particle mass in Abacus_pngbase: {m_p:.3e} h^-1 Msun')
    return m_p

def masked_non_positive_Np(Np):
    # remove zeros and any non-positive entries from halo_masses
    mask = Np > 0
    n_removed = Np.size - mask.sum()
    if n_removed:
        print(f"Removed {n_removed} non-positive halo masses")

    Np_masked = Np[mask]
    return Np_masked

def read_halo_mass(sim_name, z, sim_dir=None, m_p=None):
    cat = CompaSOHaloCatalog(sim_dir+sim_name+f'/halos/z{z:.3f}', fields=['N'])
    Np = cat.halos['N']
    Np = masked_non_positive_Np(Np)
    hm = Np * m_p
    return hm

if __name__ == "__main__":
    sim_dir = '/global/cfs/projectdirs/desi/cosmosim/Abacus/'
    sim_names = ['Abacus_pngbase_c302_ph000', 'Abacus_pngbase_c302_ph001', 'Abacus_pngbase_c300_ph000']
    labels = ['fNL=100, c302_ph000', 'fNL=100, c302_ph001', 'fNL=30, c300_ph000']
    zbins = [0.5, 0.725, 0.95, 1.25, 1.55, 2.0, 2.5, 3.0]
    
    m_p = read_particle_mass()
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 6))
    axes = axes.flatten()
    for i, z in enumerate(zbins):
        ax = axes[i]
        for sim_name, label in zip(sim_names, labels):
            mass = read_halo_mass(sim_name, z, sim_dir=sim_dir, m_p=m_p)
            ax.hist(np.log10(mass), bins=20, label=label, histtype='step', linewidth=1.5)
        ax.set_yscale('log')
        ax.set_xlabel(r'$\log(\frac{M_{\rm h}}{h^{-1} M_\odot})$')
        ax.set_ylabel('Number of Halos')
        ax.set_title(f'HMF at z={z}')
        ax.legend()
    plt.tight_layout()
    fn = 'hmf_comparison.png'
    plt.savefig(fn)
    print(f'[plot] -> {fn}')
    