# Full notes about HIP of PNG bias

*HIP: HOD-Informed Prior
*PNG: primordial non-Gaussianity
*HOD: Halo Occupation Distribution

## What we know

- It seems that we 'see' this claim: "HOD models without secondary properties always give $p=1$", but not  understand why quite well.
- Only observe that the distrubution of $p$ changes for high-z QSOs once concentration is considered in HOD fitting.

## What we do NOT know

Questions to find out soon:

- [ ] Does LRG alway has $p=1$ even in `base-A` HOD model?
- [ ] How the HIP of $p$ influence the inference of $f_{\rm NL}$, is the KP pipeline biased?
    - [ ] test on AbacusHOD mock itself?
    - [ ] test on blinded data
    - [ ] test on unblinded data

Questions remained to find out:

- [ ] HOD models without secondary properties always give $p=1$? May need to verify this with additional tests, or may try to understand why this is the case from theoritical perspective.
- [ ] use light-cones to study redshift evolution of $p$ for `base-A` HOD model.
- [ ] the influnce of redshift error, just add the EDR data or model it.
- [ ] how covariance influnce the inference of $p$?

---

Follows are details:

## Inference 


## Mock Generate

Our inference is based on several PNG mocks, generated from the AbacusPNG simulations. 
We first fit the HOD models to the small scale clusterings of DESI Y3 LRGs and QSOs. 
Then we use the best-fit HOD parameters to populate galaxies in the PNG simulations, and generate lightcone mocks with `cutsky` code if needed.

The cosmology of our mocks can be find [here](https://github.com/abacusorg/AbacusSummit/tree/main/Cosmologies/abacus_cosm000).

### Observational Data

We use the DESI Y3 LRGs and QSOs for HOD fitting.

- the clustering... 
- the $n(z)$...

### HOD 


### Lightcone

We use `cutsky` code to generate lightcone mock. 
- The original version is [here](https://github.com/cheng-zhao/cutsky). The modified version we use is [here](https://github.com/SiyiZhao/cutsky).
- We modify the rotation parameters `DESI_NGC_RA_SHIFT` and `DESI_SGC_RA_SHIFT` from 60 to 65 to avoid the overleap of DESI Y5 footprint in a $(6{~\rm Gpc}/h)^3$ box (the size of our EZmocks). 