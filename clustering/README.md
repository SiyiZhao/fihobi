# Measure the clustering 

We use the script `xirunpc.py` used in DESI to measure the clustering of the galaxy catalogs.
The original of this script can be found at `LSS/scripts/xirunpc.py`, we only change the `sedges` to measure the small-scale clustering.

Pre-requisites:
- [LSS](https://github.com/desihub/LSS): This code only works on NERSC, in the DESI environment. 

We try the following measurements:
- log-bin, s=0.01-30 Mpc/h (notice clustering measurement at s>40Mpc/h is forbidden before the key project is finished.) 
  - It shows that the clustering at s>0.1 Mpc/h is reliable. ![](plot/Y3_smin.png)
  - It also shows that different definations of $s$ can change $s^2 \xi_0$ plot. So when used to fit HOD models, we should keep the same defination of the bin center. ![](plot/Y3_test.png)
