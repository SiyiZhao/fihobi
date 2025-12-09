# fihobi: $f_{\rm NL}$-inference with HOD-informed $b_\phi$-prior 

This repo. is under active development. If you have any questions, please contact the author. 

## Repo. Structure

- `hod-variation/`: for **HOD fitting**, refer to DESI DR2 small scale clusterings ($w_p, \xi_0, \xi_2$) of LRGs and QSOs.
  - **products:**
    - *chains of HOD parameters* (with the triangle plot and the best-fit clustering plot) @ pscratch/desi-dr2-hod/QSO-xxx
    - *best-fit HOD mocks* (with the clustering measurements) @ pscratch/desi-dr2-hod/mocks -- input for `mock-data-cov/`
  - **post-analysis products:** comparison of fittings for each sample among different simulations / HOD models. The triangle plots and best-fit clustering plots @ hod-variation/output.
- `mock-data-cov/`: measure **power spectrum of AbacusPNG mocks**, generate EZmocks for **covariance** matrix.
  - **products:**
    - *power spectrum of AbacusPNG mocks* @ pscratch/desi-dr2-hod/mocks
    - *power spectrum of EZmocks* @ pscratch/EZmock/output/mocks/QSO-zx_c3xx
  - **biproducts:** 
    - *bispectrum of AbacusPNG mocks* (generated when calibrate EZmock, won't save)
- `inference/`: 

## Environment

See `env/README.md` for details. Run `source env/env.sh` to set up the environment variables whenever you start a new shell.

