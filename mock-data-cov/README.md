# Mock Data and Covariance

In this directory, we 
1. measure the clusterings of AbacusPNG mocks, 
2. use the clusterings to calibrate the parameters of EZmock, (this part is underway with the help of Zhuoyang Li & Yunyi Tang),
3. and then generate EZmocks power spectrum multipoles for the covariance matrix.

## Measure AbacusPNG mocks

Please refer to `meas_abacus.sh` for the script, where we measure the power spectrum monopole and quadrupole by `pypower` package.
- Except saving the multipoles (`class PowerSpectrumMultipole` in `pypower`) in `npy` format, we also save them in `txt` file with `powspec` format for EZmock calibration.

## Generate EZmocks for covariance matrix

Please refer to `genEZmocks.sh` for the script, where we generate EZmocks with PNG initial conditions by `genEZmockPNG.py`.

- `sleep 1` 52:39 for 500 realizations.
- no `sleep` 53:39 for 500 realizations.


## Other Works 

### test-z4

Take QSO-z4 sample as an example, we test different cases of HOD fitting and mock generation, as well as the EZmocks, by comparing the mock power spectra. Please refer to the [README](test-z4/README.md) there for details.

### measure power spectrum of EZmocks

We also have an example of measuring the power spectrum multipoles of exist EZmocks, refer `pkEZmocks.sh`.

But now we have added the `pypower` measurement part in `genEZmockPNG.py`, so this script is not necessary any more.