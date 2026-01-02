# Redshift Uncertainty 

We consider the redshift uncertainty in some of the HOD fittings.

Following Jiaxi & Shengyu's work, we generate the probability cumulative distribution function (CDF) of the redshift uncertainty $\log_{10}|dv|$ (in km/s) from the repeat observation data.

## Usage

Simply set `tracer`, redshift bins and `output_dir` in `generate_cdf.py`, then run the script to get the results saved in `output_dir`.

The codes depend on the packages and data in DESI, so it is recommended to run it on NERSC, otherwise please contact the authors.
