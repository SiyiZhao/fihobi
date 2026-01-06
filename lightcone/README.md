# Generate Lightcone

We use cutsky to generate the lightcone.

## Workflow

Assuming working in the `lightcone/` directory:
1. run `prep_nz.py` to prepare the target n(z) file. (After modify the path in the script as needed.)
2. change the parameters in `prep_cutsky.py` as needed, including the input catalog path, workdir, galactic cap, n(z) file path, redshift range, etc.
3. run `prep_cutsky.py` to prepare the cutsky configuration file and the input catalog in the required format.
```sh
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main # for mockfactory
python prep_cutsky.py
```
4. run cutsky following the output instruction printed by `prep_cutsky.py`.

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