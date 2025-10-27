# Inference

We run inference with [desilike](https://github.com/cosmodesi/desilike). 


The standard analysis pipeline fixes $p=1$ for LRG and $p=1.6$ for QSO. 
However, we want to test whether the data^[small scale clusterings for each tracer and each redshift bin] prefer different values of $p$. To do this, we run inference with $p$ as a free parameter while fix $f_{\rm NL}$ to the simulation settings.

## Box tests

### QSOs at z2.0, fNL=30

In `tests/`, we compare 3 different settings of HOD model (w/o dv, w/ dv, w/ dv and cut 3 small scale bins), and run inference for each setting. The results of $p$ are quite same to each other.

### LRGs at z0.5, fNL=30

![](out/fit_p_LRG_z0p5_triangle.png)

![](out/fit_p_LRG_z0p5_power_spectrum.png)

