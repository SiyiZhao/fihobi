# Full notes about HIP of PNG bias

*HIP: HOD-Informed Prior
*PNG: primordial non-Gaussianity
*HOD: Halo Occupation Distribution

## What we know

- It seems that we 'see' this claim: "HOD models without secondary properties always give $p=1$", but not  understand why quite well.
- Only observe that the distrubution of $p$ changes for high-z QSOs once concentration is considered in HOD fitting. -- not quite, could also occur for QSOs at lower z depending on the HOD model and fitting strategy...
- The accuracy of covariance has small influence on the inference of $f_{\rm NL}$ (in our test cases, $\lesssim 0.2 \sigma$).

## What we do NOT know

Questions to find out soon:

- [x] Does LRG alway has $p=1$ even in `base-A` HOD model? --No. 
- [ ] How the HIP of $p$ influence the inference of $f_{\rm NL}$, is the KP pipeline biased?
    - [x] test on AbacusHOD mock itself
    - [ ] test on blinded data
    - [ ] test on unblinded data
- [ ] How does the redshift error change the HIP of $p$? To test, we need to fit the HOD models with redshift error implemented, then generate PNG mocks without redshift error to infer $p$. If the influence is important, should we combine the $p$ distribution from the two cases (HOD fitting with/without redshift error) to get a more robust HIP of $p$?

Questions remained to find out:

- [ ] HOD models without secondary properties always give $p=1$? May need to verify this with additional tests, or may try to understand why this is the case from theoritical perspective.
- [ ] use light-cones to study redshift evolution of $p$ for `base-A` HOD model.
- [ ] test OQE weight.
- [ ] the influnce of redshift error, just add the EDR data or model it.
- [ ] how covariance influnce the inference of $p$?
- [ ] We now perform the inference of $p$ with the mocks in redshift space, what about the real space?

---

Follows are details:

## WorkFlows

To get the HIP of $p$, we have the following workflows:
1. measure the small scale clustering of observational data (DESI Y3 LRGs and QSOs).
2. fit the HOD models to the small scale clustering to get the HOD posterior.
3. generate the PNG mocks with the HOD posterior 
4. infer $p$ with the PNG mocks to get the HIP of $p$.

After that, we perform a series of "Mock Challenge" to test our HIP, by inferring $f_{\rm NL}$ with the HIP.
1. box level:
2. lightcone level:
3. on blinded data:
4. on unblinded data:

## Inference 

- We fix $f_{\rm NL}$ to the simulation settings to infer the HIP of $p$.
- Though in some HOD fittings we implement the redshift errors, the mocks used for the $p$ inference should NOT contain redshift errors.
    

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