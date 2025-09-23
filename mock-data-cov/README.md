# Mock Data and Covariance

In this directory, we 
1. measure the clusterings of AbacusPNG mocks, 
2. use the clusterings to calibrate the parameters of EZmock, (the calibrations are performed elsewhere, mainly done by Zhuoyang Li),
3. and then generate EZmocks power spectrum multipoles for the covariance matrix.

## Measure AbacusPNG mocks

Please refer to `meas_abacus.sh` for the script, where we measure the power spectrum monopole and quadrupole by `pypower` package.
- Except saving the multipoles (`class PowerSpectrumMultipole` in `pypower`) in `npy` format, we also save them in `txt` file with `powspec` format for EZmock calibration.