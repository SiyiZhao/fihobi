# fit $f_{\rm NL}$ with HIP of $p$

We get a HOD-Informed Prior (HIP) of $p$ from simulations. 
Currently, we use a Gaussian prior of $p$ with mean and covariance estimated from the HIP samples.

To run an inference of $f_{\rm NL}$ with HIP of $p$, follow the steps below:
1. Go `fit_fNL_HIP.sh`, modify `odir` to your desired output directory.
2. Go `prep_config.py`, modify the configuration parameters as needed.
3. Run `fit_fNL_HIP.sh` to start the inference.
