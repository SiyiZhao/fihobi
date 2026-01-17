#!/usr/bin/env python3
# from Cheng Zhao, updated
import numpy as np
import pandas as pd

def write_random_catalog(ofile, num, Lbox, chunk_size=int(1e7), seed=42):
  rng = np.random.default_rng(seed)
  buf = np.empty((chunk_size, 3), dtype=np.float32)

  with open(ofile, 'w', buffering=64*1024*1024) as f:
    for i in range(0, num, chunk_size):
      n = min(chunk_size, num - i)
      rng.random((n, 3), dtype=np.float32, out=buf[:n])
      buf[:n] *= np.float32(Lbox)
      pd.DataFrame(buf[:n]).to_csv(f, index=False, float_format='%.8g', sep=' ', header=False)
    
if __name__ == "__main__":
  n_LRG_S = int(1.5e9)
  n_LRG_N = int(2.3e9)
  n_QSO_N = int(3.1e8)
  n_QSO_S = int(2.4e8)
  Lbox = 6000

  odir_LRG = '/pscratch/sd/s/siyizhao/fihobi/lc_test/lcmock_LRGs_fnl100_base-A/RANDOM'
  ofile_LRG_S = f'{odir_LRG}/Random_N1.5e9_L{Lbox}.dat'
  ofile_LRG_N = f'{odir_LRG}/Random_N2.3e9_L{Lbox}.dat'
  odir_QSO = '/pscratch/sd/s/siyizhao/fihobi/lc_test/lcmock_QSOs_fnl100_base-A/RANDOM'
  ofile_QSO_N = f'{odir_QSO}/Random_N3.1e8_L{Lbox}.dat'
  ofile_QSO_S = f'{odir_QSO}/Random_N2.4e8_L{Lbox}.dat'

  write_random_catalog(ofile_LRG_S, n_LRG_S, Lbox, seed=24242)
  write_random_catalog(ofile_LRG_N, n_LRG_N, Lbox, seed=14242)
  
  write_random_catalog(ofile_QSO_N, n_QSO_N, Lbox, seed=4242)
  write_random_catalog(ofile_QSO_S, n_QSO_S, Lbox, seed=34242)
