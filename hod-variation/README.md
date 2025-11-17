# HOD fitting with AbacusUtils

We fit HOD models to DESI DR2 data using AbacusUtils (modified by Hanyu).

## Work Flow

1. Prepare the data, the config files and slurm scripts (follow `prep.sh`)
2. Enter `launchers/` and submit the jobs to NERSC, the launcher scripts contain three steps: 
   1. prepare: prepare the Abacus simulations with the mode of profiles, 
   2. fitting: run nest sampling to fit the HOD model,
   3. post-process: Analyze the chains and get the best-fit parameters (follow `post.sh`, we add it into the slurm script so it will be done automatically after the MCMC sampling is done), generate mock catalogs with the best-fit HOD parameters and measure the correlation functions.
3. Analysis among different fittings (Optional): use `comp_fit.py` to compare the fitting results from different simulations / HOD models. (Pay attention the data vector should be the same among the different fittings you want to compare.)
4. NEXT: post-process has generated the best-fit catalogs, go `../mock-data-cov/` to measure the power spectrum.

## Settings

We refer to the methods of the [DR2HFAbacusMocks](https://desi.lbl.gov/trac/wiki/CrossAnalysisInfrastructureWG/LSSMocks/DR2HFAbacusMocks) (Login-in Needed), mainly on v1 since v2 is generated at the same time with this project. 

### Data 

The reference data are correlation functions measured from the catalog loa-v1.1, including:
- $w_p(r_p)$ at $r_p=0.1-32$ Mpc/h, 15 (log) bins
   - The original setting refers to DR2HFAbacusMocks is $0.03<r_p<32$ Mpc/h with 18 bins, but for QSOs at highest 2 redshift bins, there are some NAN, so we further cut the first 3 bins. We have tested that this cut does not affect the fitting results of $p$ much at the 4-th redshift bin, see `inference/` for details.
- $\xi_0(s)$ and $\xi_2(s)$ at $s=0.7-32$ Mpc/h, 10 (log) bins 
   - Same as $w_p$, we cut the first 3 bins compared to the original setting of DR2HFAbacusMocks ($0.2<s<32$ Mpc/h with 13 bins).
The covariance are Jackknife covariance from 128 regions.

### Simulation

The main analysis is based on `Abacus_pngbase_c302_ph000` (Box: 2Gpc/h, N4096, fNL=100)

### HOD models

#### Default model

For QSOs, we use the base HOD model with 5 parameters + velocity bias + redshift error effect (dv) as default. The base model is described as 
$$
\begin{aligned}
& \bar{n}_{\mathrm{cen}}^{\mathrm{QSO}}(M)=\frac{1}{2} \operatorname{erfc}\left[\frac{\log _{10}\left(M_{\mathrm{cut}} / M\right)}{\sqrt{2} \sigma}\right], \\
& \bar{n}_{\mathrm{sat}}^{\mathrm{QSO}}(M)=\left[\frac{M-\kappa M_{\mathrm{cut}}}{M_1}\right]^\alpha ,
\end{aligned}
$$
and the velocity bias is applied to both centrals and satellites when assigning the velocities:
$$
\begin{aligned}
& v^b_{x, \mathrm{cen}}=v_{x, \mathrm{halo}}+\alpha_{\mathrm{c}} \sigma_{v_x}, \\
& v^b_{x, \mathrm{sat}}=v_{x, \mathrm{halo}}+\alpha_{\mathrm{s}} \sigma_{v_x}, 
\end{aligned}
$$
where $\sigma_{v_x}$ is the 1D velocity dispersion of dark matter particles in the halo in the x-direction, velocity bias is also applied in y- and z-directions. 

Additionally, we add redshift error effect (dv) to the line-of-sight velocity (z-direction) when generating the redshift space positions. The additional velocity is drawn from the distribution measured in the repeat observations, see `redshift_error/` for details.

#### Assembly bias models

`AbacusHOD` has two types of assembly bias models, one is concentration-based, the other is environment-based. We have tested both of them.

To samplify the computation, `AbacusHOD` models the assembly bias effect by modifying the two mass scales, $M_{\rm cut}$ and $M_1$, as
$$
\begin{aligned}
\log_{10} M_{\mathrm{cut}}^{\mathrm{mod}}&=\log_{10} M_{\mathrm{cut}}+A_c\left(c^{\mathrm{rank}}-0.5\right)+B_c\left(\delta^{\mathrm{rank}}-0.5\right), \\
\log_{10} M_1^{\mathrm{mod}}&=\log_{10} M_1+A_s\left(c^{\mathrm{rank}}-0.5\right)+B_s\left(\delta^{\mathrm{rank}}-0.5\right),
\end{aligned}
$$
where $A$ and $B$ are the parameters to control the strength of concentration-based and environment-based assembly bias, respectively. $c^{\mathrm{rank}}$ and $\delta^{\mathrm{rank}}$ are the rank of concentration and environment among halos in a narrow mass bin, scaled to $[0,1]$.


### Likelihood

Our likelihood contains two parts, the main part is from the correlation functions, and an additional part from the number density constraint if the HOD could not generate enough galaxies.

$$\mathcal{L} = -\frac{1}{2}(\chi_{\xi}^2 + \chi_{n_g}^2),$$
where
$$\chi_{\xi}^2=\left(\xi_{\text {model }}-\xi_{\text {data }}\right)^T \boldsymbol{C}^{-1}\left(\xi_{\text {model }}-\xi_{\text {data }}\right),$$
and
$$\chi_{n_g}^2= \begin{cases}\left(\frac{n_{\text {mock }}-n_{\text {data }}}{\sigma_n}\right)^2 & \left(n_{\text {mock }}<n_{\text {data }}\right), \\ 0 & \left(n_{\text {mock }} \geq n_{\text {data }}\right) .\end{cases}$$
The $\sigma_n$ is set to be 10% of $n_{\text {data }}$.

Note in some early fittings, we also include the punishment when $n_{\text {mock }}$ is larger than $n_{\text {data }}$, but it should not affect the results much.

### Sampler

We use `pyMultiNest` as the sampler, with 500 live points and the tolerance set to 0.5.

## Works have been done with these codes 

1. QSO z=0.8-2.1 ('z0' in our notation), on `AbacusSummit_base_c000_ph000` (fiducial cosmology), base HOD model with dv (redshift error).
2. QSO z=1.7-2.3 ('z4'), on `AbacusSummit_base_c000_ph000`, base HOD model without dv. (rerun with right number density & larger prior)
3. QSO z=1.7-2.3 ('z4'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model without dv.
4. QSO z=1.7-2.3 ('z4'), on `AbacusSummit_base_c000_ph000`, base HOD model with dv.
5. QSO z=1.4-1.7 ('z3'), on `AbacusSummit_base_c000_ph000`, base HOD model w/ & w/o dv.
6. QSO z=0.8-1.1 ('z1'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
7. QSO z=1.1-1.4 ('z2'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
8. QSO z=1.4-1.7 ('z3'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
9. QSO z=1.7-2.3 ('z4'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
10. same as 7, but cut 3 more bins at small scales in wp (from 6) and xi (from 11).
11. same as 9, but cut 3 more bins at small scales in wp (from 6) and xi (from 11).
12. QSO z=2.3-2.8 ('z5') and z=2.8-3.5 ('z6'), start from the 6th rp and 11th s bin (noted as 'rp6s11'), on `Abacus_pngbase_c300_ph000` ($f_{\rm NL}=30$), base HOD model with dv.
13. QSO at all 6 redshift bins ('z1', 'z4', 'z6' would have different prior on logM1), in 'rp6s11' mode, on `AbacusSummit_base_c302_ph000`($f_{\rm NL}=100$), base HOD model w/ & w/o dv.



## Pre-requisites

### AbacusUtils

We need the package `AbacusUtils` to read the files of the N-body simulation data products. 
AbacusHOD is a part of this package.
For DESI members, refer to the [wiki](https://desi.lbl.gov/trac/wiki/CosmoSimsWG/Abacus#AbacusSummit).

On `NERSC`, in brief, we may need first load the **environment** by 
```sh
source /global/common/software/desi/desi_environment.sh
```
Then git cloned my fork of `abacusutils` to `$HOME/lib` (or any other place you like) and finally install it.
```sh
git clone https://github.com/SiyiZhao/abacusutils.git
cd abacusutils
pip install -U -e ./
```

==Attention==: We modified it with Hanyu's `hod-variation` [repo](https://github.com/ahnyu/hod-variation/) to enable the use of `use_profiles` (assign satellites with NFW profile) and `want_dv` (add redshift error effect to `z` in RSD mocks) options. So we recommend to use my forked repo. 
(I have also small modifications to Hanyu's code to make sure the codes in this project work well in `desi_enviroment` without virtual environment.)

### CorrFunc

`AbacusUtils` uses `CorrFunc` to compute the correlation functions. [Corrfunc](https://github.com/manodeep/Corrfunc) can be easily installed by following the [guide in ReadMe](https://github.com/manodeep/Corrfunc?tab=readme-ov-file#method-1-source-installation-recommended).

I installed it into `$HOME/lib` and added the path to the enviroment variable `PYTHONPATH`:
```sh
export PYTHONPATH=$PYTHONPATH:$HOME/lib
```

## Others

- On NERSC, in order to reach out the results easily, I have create a link by `ln -sT /pscratch/sd/s/siyizhao/desi-dr2-hod /global/homes/s/siyizhao/projects/fihobi/hod-variation/output/desi-dr2-hod`, so you can find the output files in `./output/desi-dr2-hod/`.