# ECCOV4r5_WMT
This repository contains Python code to conduct the analysis and produce the figures in "Sensitivity of Southern Ocean surface transformation rates to Antarctic sea ice variability."

ECCO Version 4, release 5 (V4r5) is available [here](https://github.com/MITgcm-contrib/llc_hires/tree/master/llc_90/ecco_v4r5). We run V4r5 to obtain monthly outputs from January 1992-November 2024 at 1 degree of the following fields:
  - oceFWflx
  - SIatmFW
  - oceQnet
  - THETA
  - SALT

Scripts in this repository:
- **v4r5_wmt_func.py**: WMT helper functions
- **ECCO_WMT_paper_annual.ipynb**: Figs. 1b, 2a-b, 3a-d, S3
- **ECCO_WMT_paper_correlationcalc.ipynb**: load data necessary to make Figs. 4a-d, S4a
  - This needs to be run 3x: once per $\sigma_2$ range (sea ice formation, melt, whole SIZ) to produce the necessary .npz files (slopes_rs_formation.npz, slopes_rs_melt.npz, slopes_rs_wholeSIZ.npz) to produce Figs. 4a-d, S4a in ECCO_WMT_paper_monthly.ipynb
- **ECCO_WMT_paper_monthly.ipynb**: Figs. 4a-h, S4a-c

Other files/figures:
- **ECCO_GRID_v4r5.nc**: V4r5 grid details (in netCDF file format).
- **ecco_v4r5_1deg_areas.pkl**: V4r5 1 degree grid cell areas.
- **basin_mask_regridded_ecco_v4r5_1deg.nc**: Basin mask used to filter for the Southern Ocean ("SO") and the global ocean ("TOT").
- **slopes_rs_wholeSIZ.npz**: Contains monthly $A'$, $F_b'$, and SIE and their correlations in the whole sea ice zone used in this study ($\sigma_2 = [1035.60, 1037.25]$ $\text{kg m}^{-3}$). Created in ECCO_WMT_paper_correlationcalc.ipynb.
- **slopes_rs_melt.npz**: Contains monthly $A'$, $F_b'$, and SIE and their correlations in the sea ice melt region used in this study ($\sigma_2 = [1035.95, 1036.70]$ $\text{kg m}^{-3}$). Created in ECCO_WMT_paper_correlationcalc.ipynb.
- **slopes_rs_formation.npz**: Contains monthly $A'$, $F_b'$, and SIE and their correlations in the sea ice formation region used in this study ($\sigma_2 = [1036.79, 1037.25]$ $\text{kg m}^{-3}$). Created in ECCO_WMT_paper_correlationcalc.ipynb.
- **manuscript_figs**: Contains all figures and supplemental figures included in the manuscript.