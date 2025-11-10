# Mock Data and Covariance

Here we prepare the data and covariance for the PNG inferences.

The main tasks:
1. Measure the power spectrum of AbacusPNG mocks with `pypower`. Refer to `mock_ps.sh`, where *for one sample* we measure the power spectra of best-fit HOD mocks in different settings of simulations and HOD models, and then compare them with a plot @ mock-data-cov/out
2. Calibrate the parameters of EZmock, (this part works elsewhere and with the help of Zhuoyang Li, Yunyi Tang & Cheng Zhao),
3. Generate EZmocks power spectrum multipoles for the covariance matrix. Refer to `genEZmocks.sh`. (You may want to replot with `plot_ps.py` in `scripts/` once the EZmocks are generated.)

## Measure AbacusPNG mocks

Please refer to `meas_abacus.sh` for the script, where we measure the power spectrum monopole and quadrupole by `pypower` package.
- Except saving the multipoles (`class PowerSpectrumMultipole` in `pypower`) in `npy` format, we also save them in `txt` file with `powspec` format for EZmock calibration.

## Generate EZmocks for covariance matrix

Please refer to `genEZmocks.sh` for the script, where we generate EZmocks with PNG initial conditions by `genEZmockPNG.py`.

- `sleep 1` 52:39 for 500 realizations.
- no `sleep` 53:39 for 500 realizations.
- delete write `rand_ampl` and `rand_phase` files in 2LPT code. Now no `sleep`, around 1 hour for 500 realizations with 512^3 on 4 nodes.


## Other Works 

### test-z4

Take QSO-z4 sample as an example, we test different cases of HOD fitting and mock generation, as well as the EZmocks, by comparing the mock power spectra. Please refer to the [README](test-z4/README.md) there for details.

### measure power spectrum of EZmocks

We also have an example of measuring the power spectrum multipoles of exist EZmocks, refer `pkEZmocks.sh`.

But now we have added the `pypower` measurement part in `genEZmockPNG.py`, so this script is not necessary any more.