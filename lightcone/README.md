# Generate Lightcone

We use cutsky to generate the lightcone.

## Workflow

Assuming working in the `lightcone/` directory.

### 1. Prepare the target n(z) file

Run `prep_nz.py` to prepare the target n(z) file. (After modify the path in the script as needed.)

### 2. Prepare and run `cutsky`

Please refer to `run_cutsky.sh`, you can **either** set the parameters there and directly run the script, **or** follow the following steps:
1. set the input parameters to `prep_cutsky.py` as needed, including the input catalog path, workdir, galactic cap, n(z) file path, redshift range, etc.
2. run `prep_cutsky.py` to prepare the cutsky configuration file and the input catalog in the required format.
```sh
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for mockfactory
python prep_cutsky.py
```
3. run cutsky following the output instruction printed by `prep_cutsky.py`.

### 3. Prepare Random catalog

Run `random_box.py` after modifying the parameters in the script as needed:
- Lbox: box size in Mpc/h, should be able to cover the lightcone range.
- number: 10 times the number density of galaxies in the lightcone catalog. 
    - eg. for our LRGs, the number density is $\lesssim 6\times10^{-4}$ (Mpc/h)$^{-3}$, so the random density should be $\lesssim 6\times 10^{-3}$ (Mpc/h)$^{-3}$, times the box volume $6000^3$ (Mpc/h)$^3$, the total number of randoms should be $\lesssim 1.3\times 10^{9}$. We used 2.3e9 randoms for LRGs.
        - For 2Gpc/h box, it's 4.8e6, and we have 4155184 -> 1077723, 4194074 -> 1679597, 2269763 -> 1896222 for NGC, and 4155184 -> 553684, 4194074 -> 858725, 2269763 -> 967334 for SGC, in total 10619021 -> 4653542 for NGC and -> 2379743 for SGC. ~ 2e7 -> 7e6 objects in total.
    - eg. for our QSOs, the number density is $\lesssim 4\times10^{-5}$ (Mpc/h)$^{-3}$, so the random density should be $\lesssim 4\times 10^{-4} \times 6000^3 \sim 9\times 10^{7}$.
- random seed should be different for different galactic caps and tracers.

### 4. Cutsky Random

Run `genLCrandom.sh` after modifying the parameters in the script as needed: output directory, input random catalog path, redshift range, etc.

## Notes about `cutsky` Usage

Tips: 
1. `cutsky` needs to generate the lightcone for each galactic cap (NGC & SGC) separately.
2. `cutsky` needs the input n(z) file with first two columns be (redshift, comoving number density), and the `ZMIN` and `ZMAX` must in between the redshift range of the input n(z) file. So we use `prep_nz.py` to prepare the n(z) file from the `cdirs/` data, just keeping the `zmid` and `n(z)` columns, and adding the first and last rows with (zlow, n(z)) and (zhigh, n(z)) respectively.

Inputs of `cutsky`:
- box simulation:
    - the galaxy catalog to be used to generate the lightcone. The format should be `ASCII` or `FITS`. The catalog should contain the 3D positions (x,y,z) in real space (?) and velocities (vx,vy,vz) of galaxies in the box. 
    - boxsize in Mpc/h.
- cosmology: 
    - Omega_m, 
    - Omega_Lambda (optional, default 1-Omega_m), 
    - w (Equation of State of Dark Energy, optional, default -1).
- footprint: the footprint file for NGC/SGC. The format is `.ply` file.
- galactic cap: NGC or SGC. (why need this?)
- n(z): the target n(z) to be matched in the lightcone.
- redshift range: z_min, z_max.
- output: output path. Default output file format is `ASCII`.

Outputs of `cutsky`:
ASCII file with header: # RA(1) DEC(2) Z(3) Z_COSMO(4) NZ(5) STATUS(6) RAN_NUM_0_1(7)
Refer `output.ipynb` for how to read and analyze the output lightcone catalog.