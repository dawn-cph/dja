---
layout: post
title:  ALMA archive data mining with ECOGAL
date:   2025-11-20 15:00:32 +0100
categories: imaging ALMA catalog release
tags: demo
author: Minju Lee
showOnHighlights: true
---
{% include components/tags.html %}
(This page is auto-generated from the Jupyter notebook [ecogal-dja-showcase.ipynb]({{ site.baseurl }}/assets/post_files/2025-11-20-ecogal-dja-showcase.ipynb).)
  

## Short description of the project: 
ECOGAL (**ECO**ology for **G**alaxies using **A**LMA archive and **L**egacy surveys) is an ALMA data-mining effort that uniformly reduces archival data, creates science-ready ALMA images, and links them to JWST/HST legacy datasets in well-studied survey fields.

This notebook provides an introduction to the ECOGAL catalogue, including how to query sources by position and retrieve the summary plots available for ALMA-detected galaxies with DJA spectra. The catalogue released with this post covers galaxies in the three ALMA-accessible CANDELS fields: COSMOS, GOODS-S, and UDS.

- This notebook was tested on python 3.12 version
- Some functions that are used in this notebook can be installed from : [https://github.com/mjastro/ecogal](https://github.com/mjastro/ecogal)
    * or on terminal: 
    
    `python -m pip install git+https://github.com/mjastro/ecogal.git`

> Additional documentation will be released soon. A complete description of the ALMA data reduction and catalogue construction will appear in **Lee et al. (2025; submitted)**, and should be cited when using the ECOGAL data products. Users should also cite the appropriate survey references (including ALMA project IDs) when making use of the DJA data products.




```python
%matplotlib inline
```


```python
# libraries to install
if 0:
    !python -m pip install git+https://github.com/mjastro/ecogal.git
    !pip install tabulate
    !pip install git+https://github.com/karllark/dust_attenuation.git
```


```python
# setting the libraries

import ecogal

import numpy as np
import astropy
import os,sys
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.table import Table
from astropy.utils.data import download_file
import astropy.constants as const

import matplotlib as mpl
import cmasher as cmr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from astropy.coordinates import Angle


import shapely
from shapely import Point, Polygon


import warnings
from astropy.io import fits
from astropy.wcs import WCS
warnings.filterwarnings('ignore')

import pandas as pd


# cosmology
from astropy.cosmology import FlatLambdaCDM
cosmo = FlatLambdaCDM(H0=70, Om0=0.3, Tcmb0=2.725)


CACHE_DOWNLOADS = True


print(f'astropy version: {astropy.__version__}')
```

    astropy version: 7.1.1



```python
# Set plotting style
mpl.rcParams['axes.linewidth'] = 2
mpl.rcParams['axes.labelsize'] = 20
mpl.rcParams.update({'font.family':'serif'})
mpl.rcParams.update({'xtick.major.pad': '7.0'})
mpl.rcParams.update({'xtick.major.size': '7.5'})
mpl.rcParams.update({'xtick.major.width': '1.5'})
mpl.rcParams.update({'xtick.minor.pad': '7.0'})
mpl.rcParams.update({'xtick.minor.size': '3.5'})
mpl.rcParams.update({'xtick.minor.width': '1.0'})
mpl.rcParams.update({'ytick.major.pad': '7.0'})
mpl.rcParams.update({'ytick.major.size': '7.5'})
mpl.rcParams.update({'ytick.major.width': '1.5'})
mpl.rcParams.update({'ytick.minor.pad': '7.0'})
mpl.rcParams.update({'ytick.minor.size': '3.5'})
mpl.rcParams.update({'ytick.minor.width': '1.0'})
mpl.rcParams.update({'xtick.labelsize':14})
mpl.rcParams.update({'ytick.labelsize':14})

mpl.rcParams.update({'xtick.direction':'in'})
mpl.rcParams.update({'ytick.direction':'in'})

mpl.rcParams.update({'axes.labelsize' :18})
```


```python
# to get DJA spectra information

from urllib import request

####Needed to load spectra
import msaexp
import msaexp.spectrum

#to get DJA slit information

import grizli
from grizli import utils


print(f'grizli version: {grizli.__version__}')

```

    grizli version: 1.13.2


# Catalogue data exploration

## Read the table


```python
# prior catalogue which includes all sources with flux constraints (including non-detection) based on the source positions determined by JWST/HST detection

version ='v1' #initial data release

URL_PREFIX = "https://s3.amazonaws.com/alma-ecogal/dr1"
file_cat = "ecogal_all_priors_"+version+".csv"

if 0:
    # the latest zenodo (frozen) catalogue is available here (TBD)
    # this include blind catalogue, and detection catalogue
    URL_PREFIX = "https://zenodo.org/records/XXX"

table_url = f"{URL_PREFIX}/catalogue/{file_cat}"

tab = utils.read_catalog(download_file(table_url, cache=CACHE_DOWNLOADS), format='csv')

```

### Column descriptions


```python
columns_url = f"{URL_PREFIX}/catalogue/ecogal_{version}.columns.csv"
tab_columns = utils.read_catalog(download_file(columns_url, cache=CACHE_DOWNLOADS), format='csv')

# Set column metadata
for row in tab_columns:
    col = row['column']
    if row['unit'] != '--':
        tab[col].unit = row['unit']
    if row['description'] != '--':
        tab[col].description = row['description']

tab.info()
```

    <GTable length=258455>
           name         dtype      unit                                                                                                     description                                                                                                     class     n_bad 
    ------------------ ------- ------------ ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ ------------ ------
             projectID   str14                                                                                                                                                                                                           ALMA project ID       Column      0
           target_alma   str23                                                                                           ALMA target names without space;if original ALMA program has a space for the target name this column does not include the space       Column      0
      small_mosaic_idx   int64                                                                                                                                                                   mosaic identifier if it was obtained in the mosaic mode       Column      0
                 field    str6                                                                                                                                                                                                        legacy field names       Column      0
             id_ecogal   int64                                                                                                                                                                                                          ecogal parant ID       Column      0
                id_new   str13                                                                                                                                                                            ecogal parent full ID including the field name       Column      0
             frequency float64          GHz                                                                                                                                                                                           observed frequency       Column      0
                  band    str2                                                                                                                                                                                                        observed ALMA band       Column      0
              beam_maj float64       arcsec                                                                                                                                                                        synthesized beam major axis in arcsec       Column      0
                 frame    str4                                                                                                                                                                                                               image frame       Column      0
             RA_parent float64          deg                                                                                                                                                                  prior position from JWST/HST (RA) in degree       Column      0
            Dec_parent float64          deg                                                                                                                                                                 prior position from JWST/HST (DEC) in degree       Column      0
          RA_peak_alma float64          deg                                                                                                                                                                            ALMA peak position (RA) in degree       Column      0
         Dec_peak_alma float64          deg                                                                                                                                                                            ALMA pak position (DEC) in degree       Column      0
      separation_prior float64       arcsec                                                                                                                                                     position offset between ALMA peak and the prior position       Column      0
             flux_peak float64           Jy                                                                                                                                                                                         peak ALMA flux in Jy       Column      0
                 noise float64           Jy                                                                                                                                         1-sigma noise level (after correcting for the primary beam response)       Column      0
                    sn float64                                                                                                                                                                                                                  peak SNR       Column      0
             flux_aper float64           Jy                                                                                                                                                                            flux from the aperture photometry MaskedColumn   1707
            eflux_aper float64           Jy                                                                                                                                                                      flux error from the aperture photometry       Column      0
       flux_peak_imfit float64           Jy                                                                                                                                                           peak flux from the 2D Gaussian fitting using imfit       Column      0
            flux_imfit float64           Jy                                                                                                                                                                flux from the 2D Gaussian fitting using imfit       Column      0
           eflux_imfit float64           Jy                                                                                                                                                          flux error from the 2D Gaussian fitting using imfit       Column      0
             fac_pbcor float64                                                                                                                                                              primary beam response at the position of the source;1=center       Column      0
           id_3dhst_v4 float64                                                                                                                                                                                3D-HST(ver4.0) catalogue id when available MaskedColumn 142476
            ecogal_ver    str4                                                                                                                                                                                                            ecogal version       Column      0
        zsp_best_avail float64                                                                                                                                                                                     best available spectroscopic redshift       Column      0
       zsp_best_survey    str9                                                                                                                                                                                        selected spectroscopic survey name       Column      0
                 z_ver    str4                                                                                                                                                                                                           DJA MSA version       Column      0
                 objid float64                                                                                                                                                                                                  Unique source identifier MaskedColumn 248862
                 srcid float64                                                                                                                                                                                                   Source ID from APT plan MaskedColumn 248862
                  file   str55                                                                                                                                                                                                              DJA filename MaskedColumn 248862
               grating    str5                                                                                                                                                                                                           NIRSpec grating MaskedColumn 248862
             file_phot   str44                                                                                                                                                                                   Filename of the DJA photometric catalog MaskedColumn 249835
               id_phot float64                                                                                                                                                                                 ID number in the DJA photometric cadtalog MaskedColumn 249835
                 valid    str5                                                                                                                                                                            Redshift matches best z from visual inspection       Column      0
           z_phot_eazy float64                                                                                                                                                          photometric redshift from eazypy combining 3D-HST+DJA photometry       Column      0
                 restU float64                                                                                                                                                        flux density of the rest-frame U band from the photoz (eazypy) fit       Column      0
             restU_err float64                                                                                                                                                  flux density error of the rest-frame U band from the photoz (eazypy) fit       Column      0
                 restV float64                                                                                                                                                        flux density of the rest-frame V band from the photoz (eazypy) fit       Column      0
             restV_err float64                                                                                                                                                        flux density of the rest-frame V band from the photoz (eazypy) fit       Column      0
                 restJ float64                                                                                                                                                        flux density of the rest-frame J band from the photoz (eazypy) fit       Column      0
             restJ_err float64                                                                                                                                                        flux density of the rest-frame J band from the photoz (eazypy) fit       Column      0
               mass_ez float64      solMass                                                                                                                                                                    stellar mass from the photoz (eazypy) fit       Column      0
                sfr_ez float64 solMass / yr                                                                                                                                                             star-formation rate from the photoz (eazypy) fit       Column      0
                 Av_ez float64          mag                                                                                                                                                                                   Av the photoz (eazypy) fit       Column      0
                 lmass float64      solMass                                                                                                                                                     stellar mass in log from FAST++ fit (spec-z source only) MaskedColumn      8
             l68_lmass float64      solMass                                                                                                                               68% lower boundary of stellar mass in log from FAST++ run (spec-z source only) MaskedColumn      8
             u68_lmass float64      solMass                                                                                                                               68% upper boundary of stellar mass in log from FAST++ run (spec-z source only) MaskedColumn      8
                  lsfr float64 solMass / yr                                                                                                                                              star-formation rate in log from FAST++ fit (spec-z source only) MaskedColumn      8
              l68_lsfr float64 solMass / yr                                                                                                                        68% lower boundary of star-formation rate in log from FAST++ fit (spec-z source only) MaskedColumn      8
              u68_lsfr float64 solMass / yr                                                                                                                        68% upper boundary of star-formation rate in log from FAST++ fit (spec-z source only) MaskedColumn      8
             file_alma  str137                                                                                                                                                                       ECOGAL ALMA fits file name (primary beam corrected)       Column      0
               RA_bdsf float64          deg                                                                                                                                                                        ALMA position(RA) based on PYBDSF fit MaskedColumn 255029
              DEC_bdsf float64          deg                                                                                                                                                                       ALMA position(Dec) based on PYBDSF fit MaskedColumn 255029
      Total_flux_pbcor float64           Jy                                                                                                                                     Total flux based on PYBDSF fit (corrected for the primary beam response) MaskedColumn 255029
    E_Total_flux_pbcor float64           Jy                                                                                                                               Total flux error based on PYBDSF fit (corrected for the primary beam response) MaskedColumn 255029
                 pbfac float64                                                                                                                                          ALMA primary beam response at the position of the detected source;1=phase center MaskedColumn 255029
             Peak_flux float64           Jy                                                                                                                                                 Peak flux from PYBDSF fit (before the primary beam response) MaskedColumn 255029
           E_Peak_flux float64           Jy                                                                                                                                           Peak flux error from PYBDSF fit (before the primary beam response) MaskedColumn 255029
                   Maj float64          deg                                                                                                                                                                     the FWHM of the major axis of the source MaskedColumn 255029
                 E_Maj float64          deg                                                                                                                                                the 1-sigma error on the FWHM of the major axis of the source MaskedColumn 255029
                   Min float64          deg                                                                                                                                                                     the FWHM of the minor axis of the source MaskedColumn 255029
                 E_Min float64          deg                                                                                                                                                the 1-sigma error on the FWHM of the minor axis of the source MaskedColumn 255029
                    PA float64          deg                                                                                                                                    the position angle of the major axis of the source measured east of north MaskedColumn 255029
                  E_PA float64          deg                                                                                                                                      the 1-sigma error on the position angle of the major axis of the source MaskedColumn 255029
         Maj_img_plane float64          deg                                                                                                                                                  the FWHM of the major axis of the source in the image plane MaskedColumn 255029
       E_Maj_img_plane float64          deg                                                                                                                                         the 1-sigma error of the major axis of the source in the image plane MaskedColumn 255029
         Min_img_plane float64          deg                                                                                                                                                  the FWHM of the minor axis of the source in the image plane MaskedColumn 255029
       E_Min_img_plane float64          deg                                                                                                                                         the 1-sigma error of the minor axis of the source in the image plane MaskedColumn 255029
          PA_img_plane float64          deg                                                                                                                 the position angle in the image plane of the major axis of the source measured east of north MaskedColumn 255029
        E_PA_img_plane float64          deg                                                                                                                  the 1-sigma error of the image plane of the major axis of the source measured east of north MaskedColumn 255029
        Isl_Total_flux float64           Jy                                                                                         the total integrated Stokes I flux density of the island in which the source is located (not primary beam corrected) MaskedColumn 255029
      E_Isl_Total_flux float64           Jy                                                                                                                     the 1-sigma error on the total flux density of the island in which the source is located MaskedColumn 255029
               Isl_rms float64    Jy / beam                                                                                                                                    the average background rms value of the island (derived from the rms map) MaskedColumn 255029
                S_Code    str1              a code that defines the source structure; ‘S’ = a single-Gaussian source that is the only source in the island; ‘C’ = a single-Gaussian source in an island with other sources;'M’ = a multi-Gaussian source MaskedColumn 255029
       Separation_bdsf float64       arcsec                                                                                                                                           offset between the optical counterpart (matched within 0.8 arcsec) MaskedColumn 255029


## zphot-zspec


```python
### -- getting the unique source and spec-z sources
con_dup = np.array(tab.to_pandas()['id_new'].duplicated())
tab0 = tab[~con_dup]
len(tab0)
```




    128125




```python
con_z = tab0['zsp_best_avail']>0
con_z &= tab0['z_phot_eazy']>0

con_dja = tab0['zsp_best_survey']=='dja'
con_dja_z = np.logical_and(con_dja,con_z)

plt.scatter(tab0[con_z]['zsp_best_avail'], tab0[con_z]['z_phot_eazy'], s=1, zorder=100, label='All spec-z')
plt.scatter(tab0[con_dja_z]['zsp_best_avail'], tab0[con_dja_z]['z_phot_eazy'], marker='s',facecolor='None',edgecolor='grey',alpha=0.5, label='DJA spec-z')

plt.xlabel(r'$z_{\rm spec}$')
plt.ylabel(r'$z_{\rm phot}$')
plt.legend()
```




    <matplotlib.legend.Legend at 0x331825df0>




    
![png]({{ site.baseurl }}/assets/post_files/2025-11-20-ecogal-dja-showcase_files/ecogal-dja-showcase_15_1.png)
    


# Query if there is any ALMA coverage given the position

* ALMA/ECOGAL metadata includes information of individual ALMA images such as regions, pixel scales, phase center position, etc.

* This will allow you to check the ALMA/ECOGAL coverage for your source of interest.


```python
# A complete version of the metadata

version='v1'
meta_file = "ecogal_"+version+"_metadata.fits"

table_url = f"{URL_PREFIX}/ancillary/{meta_file}"
meta = utils.read_catalog(download_file(table_url, cache=CACHE_DOWNLOADS), format='fits')
meta[:3]
```




<div><i>GTable length=3</i>
<table id="table13186731280" class="table-striped table-bordered table-condensed">
<thead><tr><th>file_alma</th><th>version</th><th>simple</th><th>bitpix</th><th>naxis</th><th>naxis1</th><th>naxis2</th><th>naxis3</th><th>extend</th><th>bscale</th><th>bzero</th><th>bmaj</th><th>bmin</th><th>bpa</th><th>btype</th><th>object</th><th>bunit</th><th>equinox</th><th>radesys</th><th>lonpole</th><th>latpole</th><th>pc1_1</th><th>pc2_1</th><th>pc3_1</th><th>pc1_2</th><th>pc2_2</th><th>pc3_2</th><th>pc1_3</th><th>pc2_3</th><th>pc3_3</th><th>ctype1</th><th>crval1</th><th>cdelt1</th><th>crpix1</th><th>cunit1</th><th>ctype2</th><th>crval2</th><th>cdelt2</th><th>crpix2</th><th>cunit2</th><th>ctype3</th><th>crval3</th><th>cdelt3</th><th>crpix3</th><th>cunit3</th><th>pv2_1</th><th>pv2_2</th><th>restfrq</th><th>specsys</th><th>altrval</th><th>altrpix</th><th>velref</th><th>telescop</th><th>observer</th><th>date-obs</th><th>timesys</th><th>obsra</th><th>obsdec</th><th>obsgeo-x</th><th>obsgeo-y</th><th>obsgeo-z</th><th>instrume</th><th>distance</th><th>mpiprocs</th><th>chnchnks</th><th>memreq</th><th>memavail</th><th>useweigh</th><th>date</th><th>origin</th><th>almaid</th><th>is_mosaic</th><th>band</th><th>footprint</th><th>release</th><th>is_available</th><th>ra_center</th><th>dec_center</th><th>noise_fit</th><th>noise_tot</th><th>FoV_sigma</th></tr></thead>
<thead><tr><th>bytes137</th><th>bytes4</th><th>bool</th><th>int64</th><th>int64</th><th>int64</th><th>int64</th><th>int64</th><th>bool</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>bytes9</th><th>bytes26</th><th>bytes7</th><th>float64</th><th>bytes4</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>bytes8</th><th>float64</th><th>float64</th><th>float64</th><th>bytes3</th><th>bytes8</th><th>float64</th><th>float64</th><th>float64</th><th>bytes3</th><th>bytes4</th><th>float64</th><th>float64</th><th>float64</th><th>bytes2</th><th>float64</th><th>float64</th><th>float64</th><th>bytes4</th><th>float64</th><th>float64</th><th>int64</th><th>bytes4</th><th>bytes15</th><th>bytes26</th><th>bytes3</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>bytes4</th><th>float64</th><th>int64</th><th>int64</th><th>float64</th><th>float64</th><th>bool</th><th>bytes26</th><th>bytes30</th><th>bytes14</th><th>bool</th><th>int64</th><th>bytes461</th><th>bytes3</th><th>bool</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th></tr></thead>
<tr><td>2011.0.00064.S___concat_all_6_AzTEC-3_0_b7_cont_noninter2sig.image.pbcor.fits</td><td>v1.0</td><td>True</td><td>-32</td><td>3</td><td>1600</td><td>1600</td><td>1</td><td>True</td><td>1.0</td><td>0.0</td><td>0.0002005813188023</td><td>0.0001579564147525</td><td>-53.50122070312</td><td>Intensity</td><td>AzTEC-3</td><td>Jy/beam</td><td>2000.0</td><td>FK5</td><td>180.0</td><td>2.586833336311</td><td>1.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>1.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>1.0</td><td>RA---SIN</td><td>150.0890000048</td><td>-2.777777777778e-05</td><td>801.0</td><td>deg</td><td>DEC--SIN</td><td>2.586833336311</td><td>2.777777777778e-05</td><td>801.0</td><td>deg</td><td>FREQ</td><td>296763686486.8</td><td>15646751913.56</td><td>1.0</td><td>Hz</td><td>0.0</td><td>0.0</td><td>296763686486.8</td><td>LSRK</td><td>-0.0</td><td>1.0</td><td>257</td><td>ALMA</td><td>riechers</td><td>2012-04-11T01:22:13.632000</td><td>UTC</td><td>150.0890000048</td><td>2.586833336311</td><td>2225142.180269</td><td>-5440307.370349</td><td>-2481029.851874</td><td>ALMA</td><td>0.0</td><td>1</td><td>1</td><td>0.12359619</td><td>150.23436</td><td>False</td><td>2023-11-14T12:19:42.442402</td><td>CASA 6.5.6-22 CASAtools:v1.0.0</td><td>2011.0.00064.S</td><td>False</td><td>7</td><td>((150.088583,2.582778),(150.085914,2.584167),(150.084940,2.587250),(150.086331,2.589917),(150.089417,2.590889),(150.092086,2.589500),(150.093060,2.586417),(150.091669,2.583750),(150.088583,2.582778))</td><td>N/A</td><td>True</td><td>150.0890000048</td><td>2.5868333363110025</td><td>4.46259777172499e-05</td><td>5.5606829846510664e-05</td><td>8.332485222950787</td></tr>
<tr><td>2011.0.00064.S___concat_all_6_AzTEC-3_1_b7_cont_noninter2sig.image.pbcor.fits</td><td>v1.0</td><td>True</td><td>-32</td><td>3</td><td>1600</td><td>1600</td><td>1</td><td>True</td><td>1.0</td><td>0.0</td><td>0.0002007880806923</td><td>0.0001580240825812</td><td>-53.53054428101</td><td>Intensity</td><td>AzTEC-3</td><td>Jy/beam</td><td>2000.0</td><td>FK5</td><td>180.0</td><td>2.588527777932</td><td>1.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>1.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>1.0</td><td>RA---SIN</td><td>150.0868750002</td><td>-2.777777777778e-05</td><td>801.0</td><td>deg</td><td>DEC--SIN</td><td>2.588527777932</td><td>2.777777777778e-05</td><td>801.0</td><td>deg</td><td>FREQ</td><td>296763687761.7</td><td>15646752334.74</td><td>1.0</td><td>Hz</td><td>0.0</td><td>0.0</td><td>296763687761.7</td><td>LSRK</td><td>-0.0</td><td>1.0</td><td>257</td><td>ALMA</td><td>riechers</td><td>2012-04-11T01:22:54.720000</td><td>UTC</td><td>150.0868750002</td><td>2.588527777932</td><td>2225142.180269</td><td>-5440307.370349</td><td>-2481029.851874</td><td>ALMA</td><td>0.0</td><td>1</td><td>1</td><td>0.12359619</td><td>150.1451</td><td>False</td><td>2023-11-14T13:30:14.601414</td><td>CASA 6.5.6-22 CASAtools:v1.0.0</td><td>2011.0.00064.S</td><td>False</td><td>7</td><td>((150.086458,2.584472),(150.083789,2.585861),(150.082815,2.588944),(150.084206,2.591611),(150.087292,2.592583),(150.089961,2.591194),(150.090935,2.588111),(150.089544,2.585444),(150.086458,2.584472))</td><td>N/A</td><td>True</td><td>150.0868750002</td><td>2.5885277779320006</td><td>6.49289000021855e-05</td><td>0.00011714215361280367</td><td>8.33248518715434</td></tr>
<tr><td>2011.0.00097.S___concat_all_10_COSMOSLowz_64_29_b7_cont_noninter2sig.image.pbcor.fits</td><td>v1.0</td><td>True</td><td>-32</td><td>3</td><td>1844</td><td>1844</td><td>1</td><td>True</td><td>1.0</td><td>0.0</td><td>0.0001445855862565</td><td>0.0001385951704449</td><td>32.57455062866</td><td>Intensity</td><td>COSMOSLowz_64</td><td>Jy/beam</td><td>2000.0</td><td>FK5</td><td>180.0</td><td>2.193778888889</td><td>1.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>1.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>1.0</td><td>RA---SIN</td><td>150.0951</td><td>-2.777777777778e-05</td><td>923.0</td><td>deg</td><td>DEC--SIN</td><td>2.193778888889</td><td>2.777777777778e-05</td><td>923.0</td><td>deg</td><td>FREQ</td><td>341959206917.1</td><td>15956638554.12</td><td>1.0</td><td>Hz</td><td>0.0</td><td>0.0</td><td>341959206917.1</td><td>LSRK</td><td>-0.0</td><td>1.0</td><td>257</td><td>ALMA</td><td>nscoville</td><td>2012-04-22T02:13:22.032000</td><td>UTC</td><td>150.0951</td><td>2.193778888889</td><td>2225142.180269</td><td>-5440307.370349</td><td>-2481029.851874</td><td>ALMA</td><td>0.0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>False</td><td>2022-01-18T10:06:48.750999</td><td>CASA 5.6.1-8</td><td>2011.0.00097.S</td><td>True</td><td>7</td><td>((150.094822,2.190251),(150.092487,2.191390),(150.091570,2.194057),(150.092709,2.196390),(150.095378,2.197307),(150.097713,2.196168),(150.098630,2.193501),(150.097491,2.191168),(150.094822,2.190251))</td><td>dr1</td><td>True</td><td>150.0951</td><td>2.1937788888889997</td><td>0.00013968738028111863</td><td>0.00014185431064106524</td><td>7.231210572315804</td></tr>
</table></div>



### Use `ecogal` function : query metata data based on the coordinates

Use [visualcheck.get_footprint](https://github.com/mjastro/ecogal/blob/7afe6412e2309356766ab7fd702a1831214abf5e/ecogal/visualcheck.py#L34) function.


```python
import ecogal.visualcheck as visualcheck
```


```python
# get the metadata via DJA
ra, dec = 34.41887, -5.21965
fp,_ = visualcheck.get_footprint(ra,dec)
```

    There are #15 ALMA projects overlapping



```python
fp['file_alma','almaid','object','band']
```




<div><i>GTable length=15</i>
<table id="table13202810800" class="table-striped table-bordered table-condensed">
<thead><tr><th>file_alma</th><th>almaid</th><th>object</th><th>band</th></tr></thead>
<thead><tr><th>bytes137</th><th>bytes14</th><th>bytes26</th><th>int64</th></tr></thead>
<tr><td>2012.1.00245.S__all_SXDF-NB2315-2_b7_cont_noninter2sig.image.pbcor.fits</td><td>2012.1.00245.S</td><td>SXDF-NB2315-2</td><td>7</td></tr>
<tr><td>2012.1.00245.S__all_SXDF-NB2315-3_b7_cont_noninter2sig.image.pbcor.fits</td><td>2012.1.00245.S</td><td>SXDF-NB2315-3</td><td>7</td></tr>
<tr><td>2013.1.00742.S__all_SXDF-B3-NB2315-FoV1_b3_cont_noninter2sig.image.pbcor.fits</td><td>2013.1.00742.S</td><td>SXDF-B3-NB2315-FoV1</td><td>3</td></tr>
<tr><td>2013.1.00781.S__all_SXDS-AzTEC23_b6_cont_noninter2sig.image.pbcor.fits</td><td>2013.1.00781.S</td><td>SXDS-AzTEC23</td><td>6</td></tr>
<tr><td>2015.1.00442.S__all_SXDS-AzTEC28_b6_cont_noninter2sig.image.pbcor.fits</td><td>2015.1.00442.S</td><td>SXDS-AzTEC28</td><td>6</td></tr>
<tr><td>2015.1.01074.S__all_UDSp_17_b7_cont_noninter2sig.image.pbcor.fits</td><td>2015.1.01074.S</td><td>UDSp_17</td><td>7</td></tr>
<tr><td>2015.1.01528.S__all_UDS.0113_b7_cont_noninter2sig.image.pbcor.fits</td><td>2015.1.01528.S</td><td>UDS.0113</td><td>7</td></tr>
<tr><td>2016.1.00434.S__all_UDS.0113_b7_cont_noninter2sig.image.pbcor.fits</td><td>2016.1.00434.S</td><td>UDS.0113</td><td>7</td></tr>
<tr><td>2017.1.00562.S__all_NB2315_b3_cont_noninter2sig.image.pbcor.fits</td><td>2017.1.00562.S</td><td>NB2315</td><td>3</td></tr>
<tr><td>2017.1.00562.S__all_NB2315_b6_cont_noninter2sig.image.pbcor.fits</td><td>2017.1.00562.S</td><td>NB2315</td><td>6</td></tr>
<tr><td>2017.1.00562.S__all_U4-16795_b9_cont_noninter2sig.image.pbcor.fits</td><td>2017.1.00562.S</td><td>U4-16795</td><td>9</td></tr>
<tr><td>2017.1.01027.S__all_U4-16504_b7_cont_noninter2sig.image.pbcor.fits</td><td>2017.1.01027.S</td><td>U4-16504</td><td>7</td></tr>
<tr><td>2017.1.01027.S__all_U4-16795_b7_cont_noninter2sig.image.pbcor.fits</td><td>2017.1.01027.S</td><td>U4-16795</td><td>7</td></tr>
<tr><td>2019.1.00337.S__all_AS2UDS0113.1_b3_cont_noninter2sig.image.pbcor.fits</td><td>2019.1.00337.S</td><td>AS2UDS0113.1</td><td>3</td></tr>
<tr><td>2021.1.00705.S__all_UDS.0113_b4_cont_noninter2sig.image.pbcor.fits</td><td>2021.1.00705.S</td><td>UDS.0113</td><td>4</td></tr>
</table></div>



# Get ALMA/ECOGAL cutouts

## Method 1. Using `ecogal`

Use [ecogal.pbcor.show_all_cutouts](https://github.com/mjastro/ecogal/blob/b8f1f842a3447aecc3ed365953184cd66a9bab98/ecogal/pbcor.py#L95) function.


```python
import ecogal.pbcor as ecogal_plot
```

### [1] JWST RGB + ALMA cutout


```python
# an example of many ALMA coverage
ra, dec = 34.41887, -5.21965
```


```python
# this example can take a while because it downloads a lot of fits files
summary_cutouts = ecogal_plot.show_all_cutouts(ra,dec)
```

    N=15
    2013.1.00742.S__all_SXDF-B3-NB2315-FoV1_b3       b3   157x 157  0.04  dx=7.57"
    2017.1.00562.S__all_NB2315_b3                    b3   313x 313  0.02  dx=7.57"
    2019.1.00337.S__all_AS2UDS0113.1_b3              b3    63x  63  0.10  dx=9.84"
    2021.1.00705.S__all_UDS.0113_b4                  b4    33x  33  0.20  dx=6.65"
    2015.1.00442.S__all_SXDS-AzTEC28_b6              b6   157x 157  0.04  dx=8.32"
    2013.1.00781.S__all_SXDS-AzTEC23_b6              b6   313x 313  0.02  dx=8.33"
    2017.1.00562.S__all_NB2315_b6                    b6   313x 313  0.02  dx=4.83"
    2016.1.00434.S__all_UDS.0113_b7                  b7   157x 157  0.04  dx=6.65"
    2012.1.00245.S__all_SXDF-NB2315-3_b7             b7   313x 313  0.02  dx=9.65"
    2015.1.01074.S__all_UDSp_17_b7                   b7   313x 313  0.02  dx=9.75"
    2015.1.01528.S__all_UDS.0113_b7                  b7   313x 313  0.02  dx=6.66"
    2012.1.00245.S__all_SXDF-NB2315-2_b7             b7   313x 313  0.02  dx=0.15"
    2017.1.01027.S__all_U4-16504_b7                  b7    63x  63  0.10  dx=9.77"
    2017.1.01027.S__all_U4-16795_b7                  b7    63x  63  0.10  dx=0.42"
    2017.1.00562.S__all_U4-16795_b9                  b9   313x 313  0.02  dx=0.06"



    
![png]({{ site.baseurl }}/assets/post_files/2025-11-20-ecogal-dja-showcase_files/ecogal-dja-showcase_29_1.png)
    



### [2] Ready-made summary file 

There are some summary png files in the repository made for sources with ALMA detection and DJA spectra (~120 unique sources in total with the first data release), which can be queried by the source position. 

* the default searching area is 0.4 arcsec, that you can change with `r_search`


```python
ra, dec = 150.14325, 2.35599	
_ = visualcheck.get_summary(ra,dec, r_search=0.5)
```

    There are #10 ALMA projects overlapping
    There are 9 ECOGAL+DJA cross-match!
    https://s3.amazonaws.com/alma-ecogal/dr1/pngs/ecogal__0_all_filters_COSMOS.60520.png
    A source found at a distance of = 0.13 arcsec


<img src="https://s3.amazonaws.com/alma-ecogal/dr1/pngs/ecogal__0_all_filters_COSMOS.60520.png" width="70%">


```python
ra, dec = 34.27751, -5.22819
_ = visualcheck.get_summary(ra,dec)
```

    There are #1 ALMA projects overlapping
    There are 1 ECOGAL+DJA cross-match!
    https://s3.amazonaws.com/alma-ecogal/dr1/pngs/ecogal__0_all_filters_UDS.104633.png
    A source found at a distance of = 0.13 arcsec


<img src="https://s3.amazonaws.com/alma-ecogal/dr1/pngs/ecogal__0_all_filters_UDS.104633.png" width="70%">

## Method 2: Getting cutouts and footprint via DJA API

* ALMA footprint can also be retrieved via DJA API: [https://grizli-cutout.herokuapp.com/](https://grizli-cutout.herokuapp.com/)
    * See also the instructions for accessing API (for other projects) : [https://dawn-cph.github.io/dja/general/api_summary/](https://dawn-cph.github.io/dja/general/api_summary/)
* The identifier for ECOCAL is `ecogal`, followed by the output mode and coordinate information `?ra=&dec=`.

There are three different output modes:

* `output=footprint` : footprint for ALMA coverage
* `output=csv` : metadata
* `output=cutout` : making a cutout image
    * for cutout module: specify ALMA file names. The file name is available in the ECOGAL catalogue or from the metadata, and the column name is `file_alma` 

### `footprint` mode
[https://grizli-cutout.herokuapp.com/ecogal?output=footprint&ra=34.48016&dec=-5.11252](https://grizli-cutout.herokuapp.com/ecogal?output=footprint&ra=34.48016&dec=-5.11252)
### `cutout` mode
Given the ALMA file name of 2015.1.01528.S__all_UDS.0424_b7_cont_noninter2sig.image.pbcor.fits

[https://grizli-cutout.herokuapp.com/ecogal?output=cutout&sx=3.&cutout_size=2.0&ra=34.48016&dec=-5.11252&file_alma=2015.1.01528.S__all_UDS.0424_b7_cont_noninter2sig.image.pbcor.fits](https://grizli-cutout.herokuapp.com/ecogal?output=cutout&sx=3.&cutout_size=2.0&ra=34.48016&dec=-5.11252&file_alma=2015.1.01528.S__all_UDS.0424_b7_cont_noninter2sig.image.pbcor.fits)


```python
from IPython.display import display, Markdown, Latex
```


```python
# getting the summary of the footprint for a given ra, dec
ra, dec = 34.48016,-5.11252
cord = SkyCoord(ra,dec, unit=(u.degree, u.degree))
ara = tab['RA_peak_alma']
adec = tab['Dec_peak_alma']
acord = SkyCoord(ara, adec, unit=(u.degree, u.degree))
#search for the matching source within 0.1 arcsec
con_pos = acord.separation(cord).arcsec<0.15
ecotb=tab[con_pos]
```


```python

#  see also the description in the https://dawn-cph.github.io/dja/blog/2025/05/01/nirspec-merged-table-v4/
#  
cutout_URL = f"https://grizli-cutout.herokuapp.com/ecogal?output=footprint&ra={ra}&dec={dec}"

ecotb['Thumb'] = [
    "<img src=\"{0}\" height=200px>".format(
        cutout_URL.format(ra,dec)
    )
    for row in ecotb
]

df = ecotb['projectID','target_alma','id_new','band','beam_maj','sn','separation_prior','zsp_best_avail','z_phot_eazy','Thumb','file_alma'].to_pandas()

display(Markdown(df.to_markdown()))
```


|    | projectID      | target_alma   | id_new     | band   |   beam_maj |    sn |   separation_prior |   zsp_best_avail |   z_phot_eazy | Thumb                                                                                                         | file_alma                                                              |
|---:|:---------------|:--------------|:-----------|:-------|-----------:|------:|-------------------:|-----------------:|--------------:|:--------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------|
|  0 | 2023.1.01520.S | 0424.0        | UDS.105062 | b4     |       0.69 |  7.08 |               0.09 |           3.5433 |       3.47313 | <img src="https://grizli-cutout.herokuapp.com/ecogal?output=footprint&ra=34.48016&dec=-5.11252" height=200px> | 2023.1.01520.S__all_0424.0_b4_cont_noninter2sig.image.pbcor.fits       |
|  1 | 2015.1.01528.S | UDS.0424      | UDS.105062 | b7     |       0.21 | 19.15 |               0.05 |           3.5433 |       3.47313 | <img src="https://grizli-cutout.herokuapp.com/ecogal?output=footprint&ra=34.48016&dec=-5.11252" height=200px> | 2015.1.01528.S__all_UDS.0424_b7_cont_noninter2sig.image.pbcor.fits     |
|  2 | 2013.1.00781.S | SXDS-AzTEC28  | UDS.105062 | b6     |       0.32 | 18.72 |               0.06 |           3.5433 |       3.47313 | <img src="https://grizli-cutout.herokuapp.com/ecogal?output=footprint&ra=34.48016&dec=-5.11252" height=200px> | 2013.1.00781.S__all_SXDS-AzTEC28_b6_cont_noninter2sig.image.pbcor.fits |


# Access the ALMA/ECOGAL image fits files
* All fits files (primary beam corrected) are available from the DJA repository (on AWS server) and a frozen version will be available on Zenodo.


```python
#getting the corresponding file name from the catalogue
#some times the file name includes special string like "+", which should be parsed to download the fits file

idx = 2
file_alma = ecotb['file_alma'][idx]
encoded_filename = file_alma.replace("+", "%2B")
```


```python
fits_URL = "https://s3.amazonaws.com/alma-ecogal/dr1/pbcor/"

almafits = fits.open(
    download_file(str(os.path.join(fits_URL, encoded_filename)), cache=True)
                    )
```


```python
img = almafits[0].data[0]
hdr = almafits[0].header
wcs_alma = WCS(hdr)

gid = tab[con_pos]['id_new'][idx]
band = tab[con_pos]['band'][idx]
zgal = tab[con_pos]['zsp_best_avail'][idx]
lmass = np.log10(tab[con_pos]['mass_ez'][idx])
sfr = tab[con_pos]['sfr_ez'][idx]

#get the noise of the map (after pb-correction)
noise = tab[con_pos]['noise'][idx]
```


```python
##################
## plotting; think about adding a function
##################

x,y,_= wcs_alma.wcs_world2pix(ra,dec,0,0)
pixsz = np.abs(hdr['CDELT1']*3600)
imsz = 1/pixsz

noise_array = noise*np.arange(4,30,3)
cutout = img[int(y-imsz):int(y+imsz),int(x-imsz):int(x+imsz)]

fig=plt.figure(1,figsize=(5,5))
ax=plt.subplot(111)

ax.imshow(cutout, origin='lower')
ax.contour(cutout, levels = noise_array, colors='white')
ax.set_title(f'{gid},{band}')
ax.text(0.55,0.95, f'z={zgal}', transform=ax.transAxes, c='white')
ax.text(0.55,0.90, f'log(Mstar/Msun)={lmass:.2f}', transform=ax.transAxes, c='white')
ax.text(0.55,0.85, f'sfr={sfr:.2f} Msun/yr', transform=ax.transAxes, c='white')



#get beam size 
bmaj = hdr['BMAJ']*3600
bmin = hdr['BMIN']*3600
pa = hdr['BPA']
theta = Angle(90+pa,'deg') 
be=mpatches.Ellipse((imsz/6.,imsz/6.),bmaj/pixsz,bmin/pixsz,angle=theta.degree,lw=1,facecolor='grey',edgecolor='black',hatch='//')
ax.add_patch(be)

```




    <matplotlib.patches.Ellipse at 0x346f95010>




    
![png]({{ site.baseurl }}/assets/post_files/2025-11-20-ecogal-dja-showcase_files/ecogal-dja-showcase_46_1.png)
    


# Access the DJA files from the information available in the catalogue


```python
## consider peak SNR>15 and DJA spectra at z>5

con_sn = tab0['sn']>15
con_sn &= tab0['zsp_best_survey']=='dja'
con_sn &= tab0['zsp_best_avail']>5

tab1 = tab0[con_sn]
filename = tab1['file'][0]
zgal = tab1['zsp_best_avail'][0]
filename, zgal
```




    ('capers-cos01-v4_prism-clear_6368_52597.spec.fits', 5.8351)




```python
# prepare a line detectionary
# ** line dictionary -- for plot purpose (you can add more)
# ** lines in AA to overplot the emission lines

lam_file = Table.read("""line, wavelength_nm
H-alpha,656.46
H-beta,486.271
H-delta,410.1734
H-gamma,434.0472
Ly-alpha,121.567
[OII],372.71
[OII],372.986
[OII],733.1
[OII],732.0
[NeIII],386.986
[OIII],496.03
[OIII],500.824
[NII],654.986
[NII],658.527
[SII],671.827
[SII],673.267
Pa-alpha,1875
Pa-beta,1282
Pa-gamma,1093.8
Br-beta,2626
HeI,1083.0
[SIII],906.9
[SIII],953.0
[CI],985.0
[PII],1188
[FeII],1257
[FeII],1640      
""", format="csv")

#lam_file = Table.read('opt_emission_lines.csv')

lines_dic = {'Ly-alpha':r'Ly$\alpha$', 'H-beta':r'H$\beta$', 'H-alpha': r'H$\alpha$ + [NII]', 
             'H-delta':r'H$\delta$','H-gamma':r'H$\gamma$', 'Na1D':'NaID',
             'Pa-alpha':r'Pa$\alpha$','Pa-beta':r'Pa$\beta$','Pa-gamma':r'Pa$\gamma$','CaIIK':'Ca II K',
             '[SiVI]':'[SiVI]','H2':r'H$_2$',
             'Br-beta':r'Br$\gamma$','MgI':'MgI','NaI':'NaI','SiI':'SiI','HI':'[FeII]+HI+FeII',#'HI':'HI'-- for grating
             'HeI':'HeI','FeII':'FeII','[FeII]':'[FeII]','[CI]':'[CI]','[PII]':'[PII]',
             '[OII]': '[OII]', '[NII]':'[NII]', '[SII]':'[SII]', '[OIII]':'[OIII]','[NeIII]':'[NeIII]',
             '[SIII]':'[SIII]'}
```


```python
lam_file
```




<div><i>Table length=27</i>
<table id="table13184612736" class="table-striped table-bordered table-condensed">
<thead><tr><th>line</th><th>wavelength_nm</th></tr></thead>
<thead><tr><th>str8</th><th>float64</th></tr></thead>
<tr><td>H-alpha</td><td>656.46</td></tr>
<tr><td>H-beta</td><td>486.271</td></tr>
<tr><td>H-delta</td><td>410.1734</td></tr>
<tr><td>H-gamma</td><td>434.0472</td></tr>
<tr><td>Ly-alpha</td><td>121.567</td></tr>
<tr><td>[OII]</td><td>372.71</td></tr>
<tr><td>[OII]</td><td>372.986</td></tr>
<tr><td>[OII]</td><td>733.1</td></tr>
<tr><td>[OII]</td><td>732.0</td></tr>
<tr><td>...</td><td>...</td></tr>
<tr><td>Pa-beta</td><td>1282.0</td></tr>
<tr><td>Pa-gamma</td><td>1093.8</td></tr>
<tr><td>Br-beta</td><td>2626.0</td></tr>
<tr><td>HeI</td><td>1083.0</td></tr>
<tr><td>[SIII]</td><td>906.9</td></tr>
<tr><td>[SIII]</td><td>953.0</td></tr>
<tr><td>[CI]</td><td>985.0</td></tr>
<tr><td>[PII]</td><td>1188.0</td></tr>
<tr><td>[FeII]</td><td>1257.0</td></tr>
<tr><td>[FeII]</td><td>1640.0</td></tr>
</table></div>



### set some functions to get DJA spectra


```python
########################################
### Load the DJA spectra information:
########################################

def loadDJAspec(file_fullpath):
    sh = msaexp.spectrum.SpectrumSampler(file_fullpath, err_median_filter=None)
    wave = np.array(sh.spec["wave"])*1e4 ###in AA
    fnu = sh.spec["flux"] ##uJy
    fnu_err = sh.spec["full_err"] ##uJy

    spec_flambda = np.array((fnu*u.uJy/(wave*u.AA)**2*const.c).to(u.erg/u.s/u.cm**2/u.AA)/(u.erg/u.s/u.cm**2/u.AA))
    spec_flambda_err = np.array((fnu_err/(wave*u.AA)**2*const.c).to(u.erg/u.s/u.cm**2/u.AA)/(u.erg/u.s/u.cm**2/u.AA))
    return(sh,wave,spec_flambda,spec_flambda_err)
```


```python

#################################################
### settting up the DJA spectra information
#################################################

def get_dja_spectra(file, zsp, restframe=False):
    #plotting in the restframe
    
    root = file.split('_')[0]+'/'
    basename = 'https://s3.amazonaws.com/msaexp-nirspec/extractions/'
    fullname = basename+root+file

    print(f'A galaxy at z={zsp}')
    sampled,lam,galaxy,noise = loadDJAspec(fullname)

    #deredshift
    lam0 = lam/(1 + zsp)
    if restframe:
        lam /=(1 + zsp) # Compute approximate restframe wavelength
    

    ####mask areas
    con_mask = noise==0 
    con_mask |= noise>galaxy[lam > 1100].max()
    galaxy_masked = np.ma.masked_where(con_mask, galaxy)


    galaxy0=galaxy_masked
    noise0=noise
    lam0=lam #in AA
    return lam0, galaxy0, noise0



        
```


```python
lam0, galaxy0, noise0 = get_dja_spectra(filename, zgal, restframe=True)
plt.plot(lam0[lam0>1300],galaxy0[lam0>1300])
plt.xlabel(f'Rest-Wavelength ($\AA$)')
plt.ylabel(f'Flux (erg/s/cm$^2$/$\AA$)')

##adding line identifiers
lines_plotted=[]
ticker_max = galaxy0.max()
text_hi = ticker_max+1e-20
for kk in range(len(lam_file)):
    lam_idx = np.argmin(np.abs(lam_file['wavelength_nm'][kk]*10-lam0))
    
    if lam_file['wavelength_nm'][kk]*10> lam0.min() and lam_file['wavelength_nm'][kk]*10<lam0.max() and noise0[lam_idx]>0:
        plt.axvline(lam_file['wavelength_nm'][kk]*10, linestyle=':', color='darkgrey')
        if lam_file['line'][kk] not in lines_plotted:
            #lines_plotted.append(lam_file['line'][kk])
            if lam_file['line'][kk] not in ['[NII]']:#if PRISM #'[FeII]','FeII'
                plt.text(lam_file['wavelength_nm'][kk]*10+0.01, text_hi*(0.9-0.1*np.mod(kk,3)), lines_dic[lam_file['line'][kk]], rotation='vertical', fontsize=9)

```

    A galaxy at z=5.8351



    
![png]({{ site.baseurl }}/assets/post_files/2025-11-20-ecogal-dja-showcase_files/ecogal-dja-showcase_54_1.png)
    


## get source information with multiple DJA spectra


```python
# Full DJA table

table_url = "https://s3.amazonaws.com/msaexp-nirspec/extractions/dja_msaexp_emission_lines_v4.4.csv.gz"
tab00 = utils.read_catalog(download_file(table_url, cache=True), format='csv')


```


```python
con_sn = tab0['sn']>10
con_sn &= tab0['zsp_best_survey']=='dja'
con_sn &= tab0['zsp_best_avail']>4

tab0[con_sn]['file','objid']
```




<div><i>GTable length=6</i>
<table id="table13184605776" class="table-striped table-bordered table-condensed">
<thead><tr><th>file</th><th>objid</th></tr></thead>
<thead><tr><th>str55</th><th>float64</th></tr></thead>
<tr><td>gto-wide-uds13-v4_prism-clear_1215_1951.spec.fits</td><td>172449.0</td></tr>
<tr><td>capers-cos01-v4_prism-clear_6368_52597.spec.fits</td><td>141884.0</td></tr>
<tr><td>rubies-uds23-v4_prism-clear_4233_166691.spec.fits</td><td>149974.0</td></tr>
<tr><td>capers-cos04-v4_prism-clear_6368_36571.spec.fits</td><td>143258.0</td></tr>
<tr><td>rubies-uds1-v4_prism-clear_4233_37108.spec.fits</td><td>151060.0</td></tr>
<tr><td>gto-wide-uds13-v4_prism-clear_1215_1472.spec.fits</td><td>162424.0</td></tr>
</table></div>




```python
## check the alternative spectra information

dja_uniq_id = 172449
print(dja_uniq_id)

#search for other dja spectra
msa = tab00[tab00['objid'] == dja_uniq_id]
msa
```

    172449





<div><i>GTable length=4</i>
<table id="table13210052288" class="table-striped table-bordered table-condensed">
<thead><tr><th>file</th><th>srcid</th><th>ra</th><th>dec</th><th>grating</th><th>filter</th><th>effexptm</th><th>nfiles</th><th>dataset</th><th>msamet</th><th>msaid</th><th>msacnf</th><th>dithn</th><th>slitid</th><th>root</th><th>npix</th><th>ndet</th><th>wmin</th><th>wmax</th><th>wmaxsn</th><th>sn10</th><th>flux10</th><th>err10</th><th>sn50</th><th>flux50</th><th>err50</th><th>sn90</th><th>flux90</th><th>err90</th><th>xstart</th><th>ystart</th><th>xsize</th><th>ysize</th><th>slit_pa</th><th>pa_v3</th><th>srcypix</th><th>profcen</th><th>profsig</th><th>ctime</th><th>version</th><th>exptime</th><th>contchi2</th><th>dof</th><th>fullchi2</th><th>line_ariii_7138</th><th>line_ariii_7138_err</th><th>line_ariii_7753</th><th>line_ariii_7753_err</th><th>line_bra</th><th>line_bra_err</th><th>line_brb</th><th>line_brb_err</th><th>line_brd</th><th>line_brd_err</th><th>line_brg</th><th>line_brg_err</th><th>line_hb</th><th>line_hb_err</th><th>line_hd</th><th>line_hd_err</th><th>line_hei_1083</th><th>line_hei_1083_err</th><th>line_hei_3889</th><th>line_hei_3889_err</th><th>line_hei_5877</th><th>line_hei_5877_err</th><th>line_hei_7065</th><th>line_hei_7065_err</th><th>line_hei_8446</th><th>line_hei_8446_err</th><th>line_heii_4687</th><th>line_heii_4687_err</th><th>line_hg</th><th>line_hg_err</th><th>line_lya</th><th>line_lya_err</th><th>line_mgii</th><th>line_mgii_err</th><th>line_neiii_3867</th><th>line_neiii_3867_err</th><th>line_neiii_3968</th><th>line_neiii_3968_err</th><th>line_nev_3346</th><th>line_nev_3346_err</th><th>line_nevi_3426</th><th>line_nevi_3426_err</th><th>line_niii_1750</th><th>line_niii_1750_err</th><th>line_oi_6302</th><th>line_oi_6302_err</th><th>line_oii</th><th>line_oii_7325</th><th>line_oii_7325_err</th><th>line_oii_err</th><th>line_oiii</th><th>line_oiii_1663</th><th>line_oiii_1663_err</th><th>line_oiii_4363</th><th>line_oiii_4363_err</th><th>line_oiii_4959</th><th>line_oiii_4959_err</th><th>line_oiii_5007</th><th>line_oiii_5007_err</th><th>line_oiii_err</th><th>line_pa10</th><th>line_pa10_err</th><th>line_pa8</th><th>line_pa8_err</th><th>line_pa9</th><th>line_pa9_err</th><th>line_paa</th><th>line_paa_err</th><th>line_pab</th><th>line_pab_err</th><th>line_pad</th><th>line_pad_err</th><th>line_pag</th><th>line_pag_err</th><th>line_pfb</th><th>line_pfb_err</th><th>line_pfd</th><th>line_pfd_err</th><th>line_pfe</th><th>line_pfe_err</th><th>line_pfg</th><th>line_pfg_err</th><th>line_sii</th><th>line_sii_err</th><th>line_siii_9068</th><th>line_siii_9068_err</th><th>line_siii_9531</th><th>line_siii_9531_err</th><th>spl_0</th><th>spl_0_err</th><th>spl_1</th><th>spl_10</th><th>spl_10_err</th><th>spl_11</th><th>spl_11_err</th><th>spl_12</th><th>spl_12_err</th><th>spl_13</th><th>spl_13_err</th><th>spl_14</th><th>spl_14_err</th><th>spl_15</th><th>spl_15_err</th><th>spl_16</th><th>spl_16_err</th><th>spl_17</th><th>spl_17_err</th><th>spl_18</th><th>spl_18_err</th><th>spl_19</th><th>spl_19_err</th><th>spl_1_err</th><th>spl_2</th><th>spl_20</th><th>spl_20_err</th><th>spl_21</th><th>spl_21_err</th><th>spl_22</th><th>spl_22_err</th><th>spl_2_err</th><th>spl_3</th><th>spl_3_err</th><th>spl_4</th><th>spl_4_err</th><th>spl_5</th><th>spl_5_err</th><th>spl_6</th><th>spl_6_err</th><th>spl_7</th><th>spl_7_err</th><th>spl_8</th><th>spl_8_err</th><th>spl_9</th><th>spl_9_err</th><th>zline</th><th>line_civ_1549</th><th>line_civ_1549_err</th><th>line_h10</th><th>line_h10_err</th><th>line_h11</th><th>line_h11_err</th><th>line_h12</th><th>line_h12_err</th><th>line_h7</th><th>line_h7_err</th><th>line_h8</th><th>line_h8_err</th><th>line_h9</th><th>line_h9_err</th><th>line_ha</th><th>line_ha_err</th><th>line_hei_6680</th><th>line_hei_6680_err</th><th>line_heii_1640</th><th>line_heii_1640_err</th><th>line_nii_6549</th><th>line_nii_6549_err</th><th>line_nii_6584</th><th>line_nii_6584_err</th><th>line_oii_7323</th><th>line_oii_7323_err</th><th>line_oii_7332</th><th>line_oii_7332_err</th><th>line_sii_6717</th><th>line_sii_6717_err</th><th>line_sii_6731</th><th>line_sii_6731_err</th><th>line_siii_6314</th><th>line_siii_6314_err</th><th>escale0</th><th>escale1</th><th>line_ciii_1906</th><th>line_ciii_1906_err</th><th>line_niv_1487</th><th>line_niv_1487_err</th><th>line_pah_3p29</th><th>line_pah_3p29_err</th><th>line_pah_3p40</th><th>line_pah_3p40_err</th><th>eqw_ariii_7138</th><th>eqw_ariii_7753</th><th>eqw_bra</th><th>eqw_brb</th><th>eqw_brd</th><th>eqw_brg</th><th>eqw_ciii_1906</th><th>eqw_civ_1549</th><th>eqw_ha_nii</th><th>eqw_hb</th><th>eqw_hd</th><th>eqw_hei_1083</th><th>eqw_hei_3889</th><th>eqw_hei_5877</th><th>eqw_hei_7065</th><th>eqw_hei_8446</th><th>eqw_heii_1640</th><th>eqw_heii_4687</th><th>eqw_hg</th><th>eqw_lya</th><th>eqw_mgii</th><th>eqw_neiii_3867</th><th>eqw_neiii_3968</th><th>eqw_nev_3346</th><th>eqw_nevi_3426</th><th>eqw_niii_1750</th><th>eqw_niv_1487</th><th>eqw_oi_6302</th><th>eqw_oii</th><th>eqw_oii_7325</th><th>eqw_oiii</th><th>eqw_oiii_1663</th><th>eqw_oiii_4363</th><th>eqw_oiii_4959</th><th>eqw_oiii_5007</th><th>eqw_pa10</th><th>eqw_pa8</th><th>eqw_pa9</th><th>eqw_paa</th><th>eqw_pab</th><th>eqw_pad</th><th>eqw_pag</th><th>eqw_pfb</th><th>eqw_pfd</th><th>eqw_pfe</th><th>eqw_pfg</th><th>eqw_sii</th><th>eqw_siii_9068</th><th>eqw_siii_9531</th><th>line_ha_nii</th><th>line_ha_nii_err</th><th>eqw_h10</th><th>eqw_h11</th><th>eqw_h12</th><th>eqw_h7</th><th>eqw_h8</th><th>eqw_h9</th><th>eqw_ha</th><th>eqw_hei_6680</th><th>eqw_nii_6549</th><th>eqw_nii_6584</th><th>eqw_oii_7323</th><th>eqw_oii_7332</th><th>eqw_sii_6717</th><th>eqw_sii_6731</th><th>eqw_siii_6314</th><th>sn_line</th><th>ztime</th><th>line_ci_9850</th><th>line_ci_9850_err</th><th>line_feii_11128</th><th>line_feii_11128_err</th><th>line_pii_11886</th><th>line_pii_11886_err</th><th>line_feii_12570</th><th>line_feii_12570_err</th><th>eqw_ci_9850</th><th>eqw_feii_11128</th><th>eqw_pii_11886</th><th>eqw_feii_12570</th><th>line_feii_16440</th><th>line_feii_16440_err</th><th>line_feii_16877</th><th>line_feii_16877_err</th><th>line_brf</th><th>line_brf_err</th><th>line_feii_17418</th><th>line_feii_17418_err</th><th>line_bre</th><th>line_bre_err</th><th>line_feii_18362</th><th>line_feii_18362_err</th><th>eqw_feii_16440</th><th>eqw_feii_16877</th><th>eqw_brf</th><th>eqw_feii_17418</th><th>eqw_bre</th><th>eqw_feii_18362</th><th>valid</th><th>objid</th><th>z_best</th><th>ztype</th><th>z_prism</th><th>z_grating</th><th>phot_correction</th><th>phot_flux_radius</th><th>phot_dr</th><th>file_phot</th><th>id_phot</th><th>phot_mag_auto</th><th>phot_f090w_tot_1</th><th>phot_f090w_etot_1</th><th>phot_f115w_tot_1</th><th>phot_f115w_etot_1</th><th>phot_f150w_tot_1</th><th>phot_f150w_etot_1</th><th>phot_f200w_tot_1</th><th>phot_f200w_etot_1</th><th>phot_f277w_tot_1</th><th>phot_f277w_etot_1</th><th>phot_f356w_tot_1</th><th>phot_f356w_etot_1</th><th>phot_f410m_tot_1</th><th>phot_f410m_etot_1</th><th>phot_f444w_tot_1</th><th>phot_f444w_etot_1</th><th>phot_Av</th><th>phot_mass</th><th>phot_restU</th><th>phot_restV</th><th>phot_restJ</th><th>z_phot</th><th>phot_LHa</th><th>phot_LOIII</th><th>phot_LOII</th><th>grade</th><th>zgrade</th><th>reviewer</th><th>comment</th><th>zrf</th><th>escale</th><th>obs_239_valid</th><th>obs_239_frac</th><th>obs_239_flux</th><th>obs_239_err</th><th>obs_239_full_err</th><th>obs_205_valid</th><th>obs_205_frac</th><th>obs_205_flux</th><th>obs_205_err</th><th>obs_205_full_err</th><th>obs_362_valid</th><th>obs_362_frac</th><th>obs_362_flux</th><th>obs_362_err</th><th>obs_362_full_err</th><th>obs_363_valid</th><th>obs_363_frac</th><th>obs_363_flux</th><th>obs_363_err</th><th>obs_363_full_err</th><th>obs_364_valid</th><th>obs_364_frac</th><th>obs_364_flux</th><th>obs_364_err</th><th>obs_364_full_err</th><th>obs_365_valid</th><th>obs_365_frac</th><th>obs_365_flux</th><th>obs_365_err</th><th>obs_365_full_err</th><th>obs_366_valid</th><th>obs_366_frac</th><th>obs_366_flux</th><th>obs_366_err</th><th>obs_366_full_err</th><th>obs_370_valid</th><th>obs_370_frac</th><th>obs_370_flux</th><th>obs_370_err</th><th>obs_370_full_err</th><th>obs_371_valid</th><th>obs_371_frac</th><th>obs_371_flux</th><th>obs_371_err</th><th>obs_371_full_err</th><th>obs_375_valid</th><th>obs_375_frac</th><th>obs_375_flux</th><th>obs_375_err</th><th>obs_375_full_err</th><th>obs_376_valid</th><th>obs_376_frac</th><th>obs_376_flux</th><th>obs_376_err</th><th>obs_376_full_err</th><th>obs_377_valid</th><th>obs_377_frac</th><th>obs_377_flux</th><th>obs_377_err</th><th>obs_377_full_err</th><th>obs_379_valid</th><th>obs_379_frac</th><th>obs_379_flux</th><th>obs_379_err</th><th>obs_379_full_err</th><th>obs_380_valid</th><th>obs_380_frac</th><th>obs_380_flux</th><th>obs_380_err</th><th>obs_380_full_err</th><th>obs_381_valid</th><th>obs_381_frac</th><th>obs_381_flux</th><th>obs_381_err</th><th>obs_381_full_err</th><th>obs_382_valid</th><th>obs_382_frac</th><th>obs_382_flux</th><th>obs_382_err</th><th>obs_382_full_err</th><th>obs_383_valid</th><th>obs_383_frac</th><th>obs_383_flux</th><th>obs_383_err</th><th>obs_383_full_err</th><th>obs_384_valid</th><th>obs_384_frac</th><th>obs_384_flux</th><th>obs_384_err</th><th>obs_384_full_err</th><th>obs_385_valid</th><th>obs_385_frac</th><th>obs_385_flux</th><th>obs_385_err</th><th>obs_385_full_err</th><th>obs_386_valid</th><th>obs_386_frac</th><th>obs_386_flux</th><th>obs_386_err</th><th>obs_386_full_err</th><th>rest_120_valid</th><th>rest_120_frac</th><th>rest_120_flux</th><th>rest_120_err</th><th>rest_120_full_err</th><th>rest_121_valid</th><th>rest_121_frac</th><th>rest_121_flux</th><th>rest_121_err</th><th>rest_121_full_err</th><th>rest_218_valid</th><th>rest_218_frac</th><th>rest_218_flux</th><th>rest_218_err</th><th>rest_218_full_err</th><th>rest_219_valid</th><th>rest_219_frac</th><th>rest_219_flux</th><th>rest_219_err</th><th>rest_219_full_err</th><th>rest_270_valid</th><th>rest_270_frac</th><th>rest_270_flux</th><th>rest_270_err</th><th>rest_270_full_err</th><th>rest_271_valid</th><th>rest_271_frac</th><th>rest_271_flux</th><th>rest_271_err</th><th>rest_271_full_err</th><th>rest_272_valid</th><th>rest_272_frac</th><th>rest_272_flux</th><th>rest_272_err</th><th>rest_272_full_err</th><th>rest_274_valid</th><th>rest_274_frac</th><th>rest_274_flux</th><th>rest_274_err</th><th>rest_274_full_err</th><th>rest_153_valid</th><th>rest_153_frac</th><th>rest_153_flux</th><th>rest_153_err</th><th>rest_153_full_err</th><th>rest_154_valid</th><th>rest_154_frac</th><th>rest_154_flux</th><th>rest_154_err</th><th>rest_154_full_err</th><th>rest_155_valid</th><th>rest_155_frac</th><th>rest_155_flux</th><th>rest_155_err</th><th>rest_155_full_err</th><th>rest_156_valid</th><th>rest_156_frac</th><th>rest_156_flux</th><th>rest_156_err</th><th>rest_156_full_err</th><th>rest_157_valid</th><th>rest_157_frac</th><th>rest_157_flux</th><th>rest_157_err</th><th>rest_157_full_err</th><th>rest_158_valid</th><th>rest_158_frac</th><th>rest_158_flux</th><th>rest_158_err</th><th>rest_158_full_err</th><th>rest_159_valid</th><th>rest_159_frac</th><th>rest_159_flux</th><th>rest_159_err</th><th>rest_159_full_err</th><th>rest_160_valid</th><th>rest_160_frac</th><th>rest_160_flux</th><th>rest_160_err</th><th>rest_160_full_err</th><th>rest_161_valid</th><th>rest_161_frac</th><th>rest_161_flux</th><th>rest_161_err</th><th>rest_161_full_err</th><th>rest_162_valid</th><th>rest_162_frac</th><th>rest_162_flux</th><th>rest_162_err</th><th>rest_162_full_err</th><th>rest_163_valid</th><th>rest_163_frac</th><th>rest_163_flux</th><th>rest_163_err</th><th>rest_163_full_err</th><th>rest_414_valid</th><th>rest_414_frac</th><th>rest_414_flux</th><th>rest_414_err</th><th>rest_414_full_err</th><th>rest_415_valid</th><th>rest_415_frac</th><th>rest_415_flux</th><th>rest_415_err</th><th>rest_415_full_err</th><th>rest_416_valid</th><th>rest_416_frac</th><th>rest_416_flux</th><th>rest_416_err</th><th>rest_416_full_err</th><th>beta</th><th>beta_ref_flux</th><th>beta_npix</th><th>beta_wlo</th><th>beta_whi</th><th>beta_nmad</th><th>dla_npix</th><th>dla_value</th><th>dla_unc</th><th>beta_cov_00</th><th>beta_cov_01</th><th>beta_cov_10</th><th>beta_cov_11</th></tr></thead>
<thead><tr><th>str57</th><th>int64</th><th>float64</th><th>float64</th><th>str5</th><th>str6</th><th>float64</th><th>int64</th><th>str72</th><th>str25</th><th>int64</th><th>int64</th><th>int64</th><th>int64</th><th>str24</th><th>int64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>int64</th><th>int64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>str30</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>str5</th><th>int64</th><th>float64</th><th>str1</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>str44</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>str4</th><th>str93</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>int64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th><th>float64</th></tr></thead>
<tr><td>excels-uds01-v4_g235m-f170lp_3543_109269.spec.fits</td><td>109269</td><td>34.35062413</td><td>-5.14987821</td><td>G235M</td><td>F170LP</td><td>6565.0</td><td>6</td><td>jw03543001001_05101_00002_nrs1_f170lp_g235m_raw.113.3543_109269.fits</td><td>jw03543001001_02_msa.fits</td><td>61</td><td>2</td><td>1</td><td>113</td><td>excels-uds01-v4</td><td>2775</td><td>1</td><td>1.6052381</td><td>4.5752573</td><td>2.8156571</td><td>0.6637892</td><td>0.18690835</td><td>0.105276756</td><td>2.2439482</td><td>0.42614815</td><td>0.17913413</td><td>4.0894103</td><td>0.8803835</td><td>0.55858326</td><td>505</td><td>1434</td><td>1544</td><td>34</td><td>0.0</td><td>56.909737</td><td>0.0</td><td>0.001</td><td>0.7432314</td><td>1737361758.0337665</td><td>0.9.4.dev7+g92b1aa6</td><td>39390.0</td><td>21056.38</td><td>2775</td><td>4609.6426</td><td>38.13521</td><td>13.5339</td><td>6.23057</td><td>15.9514675</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>421.78845</td><td>12.253539</td><td>40.8329</td><td>9.549703</td><td>--</td><td>--</td><td>--</td><td>--</td><td>77.94422</td><td>11.366782</td><td>-18.494478</td><td>14.979722</td><td>--</td><td>--</td><td>10.297021</td><td>8.836235</td><td>160.58878</td><td>9.798167</td><td>--</td><td>--</td><td>--</td><td>--</td><td>99.20305</td><td>11.2175455</td><td>33.67219</td><td>13.387148</td><td>5.13252</td><td>14.60536</td><td>-8.739283</td><td>12.896657</td><td>--</td><td>--</td><td>45.190254</td><td>16.34102</td><td>760.06665</td><td>--</td><td>--</td><td>17.633625</td><td>--</td><td>--</td><td>--</td><td>31.543615</td><td>8.97263</td><td>475.65164</td><td>12.492301</td><td>1478.7195</td><td>20.716312</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>2.6916635</td><td>1.0292606</td><td>1.7623694</td><td>1.2084138</td><td>0.15936823</td><td>0.7734618</td><td>0.109258264</td><td>1.507685</td><td>0.09797959</td><td>0.94181395</td><td>0.09681845</td><td>1.1777208</td><td>0.101651385</td><td>0.77827024</td><td>0.1148971</td><td>1.0161806</td><td>0.15089206</td><td>0.77205783</td><td>0.29294607</td><td>-0.36806196</td><td>1.5045673</td><td>-4700.389</td><td>2830.5718</td><td>0.3863113</td><td>2.5191631</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.22010241</td><td>1.9552373</td><td>0.1284232</td><td>2.357576</td><td>0.10218456</td><td>2.2045765</td><td>0.080455534</td><td>1.839689</td><td>0.07207858</td><td>1.9590814</td><td>0.071644664</td><td>1.7162542</td><td>0.07768974</td><td>1.4521762</td><td>0.08238754</td><td>4.622439</td><td>--</td><td>--</td><td>-23.880041</td><td>10.763638</td><td>-4.216068</td><td>10.945385</td><td>-10.380039</td><td>10.463703</td><td>34.730713</td><td>12.585057</td><td>63.86072</td><td>11.191996</td><td>-11.493438</td><td>10.910542</td><td>1681.4718</td><td>22.707413</td><td>-3.8843367</td><td>13.712671</td><td>--</td><td>--</td><td>92.769104</td><td>13.244619</td><td>303.3422</td><td>14.018277</td><td>32.40743</td><td>14.736954</td><td>16.250576</td><td>15.096581</td><td>101.71479</td><td>13.087306</td><td>102.27705</td><td>12.364596</td><td>-1.5309846</td><td>11.467584</td><td>-0.009823302</td><td>-0.121039405</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>33.2399</td><td>6.5497913</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>224.49889</td><td>18.628468</td><td>--</td><td>--</td><td>48.388504</td><td>-15.68925</td><td>--</td><td>--</td><td>5.4066896</td><td>80.58066</td><td>--</td><td>--</td><td>43.52189</td><td>14.867565</td><td>2.3390548</td><td>-4.0933743</td><td>--</td><td>--</td><td>30.003298</td><td>341.56543</td><td>--</td><td>--</td><td>--</td><td>15.96317</td><td>259.9941</td><td>822.1586</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-10.549018</td><td>-1.8727355</td><td>-4.633839</td><td>15.341046</td><td>28.01381</td><td>-5.052083</td><td>1117.2476</td><td>-2.8325858</td><td>61.117584</td><td>204.48856</td><td>32.12791</td><td>16.236942</td><td>77.48471</td><td>79.08182</td><td>-1.009964</td><td>74.0</td><td>1737501800.0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>True</td><td>172449</td><td>4.6228543</td><td>G</td><td>4.621582</td><td>4.6228543</td><td>1.42</td><td>5.58</td><td>0.07257426</td><td>primer-uds-north-grizli-v7.2-fix_phot.fits</td><td>39787</td><td>23.86</td><td>0.2917665994332862</td><td>0.0074583520942602035</td><td>0.375822323338598</td><td>0.007474258631804441</td><td>0.4462115844556865</td><td>0.006440427649332001</td><td>0.5739798944677847</td><td>0.0055131230600766225</td><td>0.8435675923509218</td><td>0.004741583591371624</td><td>1.0094882735221247</td><td>0.0047143753686044055</td><td>0.8893053372138517</td><td>0.007319798398806998</td><td>0.9324802470703117</td><td>0.006405565944800626</td><td>1.7697781011450084</td><td>32809883821.644165</td><td>0.50983775</td><td>0.8515203</td><td>1.7189896</td><td>4.3906884</td><td>1693531123.1206756</td><td>2439001724.140659</td><td>491718980.0611007</td><td>3</td><td>4.62244</td><td>GBr</td><td>--</td><td>4.622438759007668</td><td>0.746566883923777</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.25734946334707326</td><td>0.1074029218392234</td><td>0.13636944110351917</td><td>0.10877193379102598</td><td>2775</td><td>0.0001394147781913819</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>7.565232436087342e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>3.422394938541863e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.18365482662141527</td><td>0.08209852978824275</td><td>0.16733941953045023</td><td>0.13347483195853058</td><td>2775</td><td>0.9999855948537121</td><td>0.3193219632664132</td><td>0.005046263733122996</td><td>0.003990200871756824</td><td>2775</td><td>0.9999941843069329</td><td>0.2537792256940876</td><td>0.007393142686722595</td><td>0.0058590486168480374</td><td>2775</td><td>0.9999997834578057</td><td>0.38033510071734095</td><td>0.007166974424120975</td><td>0.005662438935784687</td><td>2775</td><td>1.0445811860385603</td><td>0.5174015331443249</td><td>0.005326151990107252</td><td>0.004123053610335878</td><td>2775</td><td>0.9592728684084484</td><td>0.674501855000472</td><td>0.010566295717687798</td><td>0.007890078518426866</td><td>2775</td><td>0.6864766461295206</td><td>0.5792201942495757</td><td>0.020225125958432014</td><td>0.014654466478661369</td><td>2775</td><td>0.9999202045997251</td><td>0.42909751937482243</td><td>0.008124019535932383</td><td>0.006308060928818762</td><td>2775</td><td>1.1339807135904223</td><td>0.39599140714595715</td><td>0.009180965975024354</td><td>0.006979044758972154</td><td>2775</td><td>0.9155759349124712</td><td>0.4344144049679926</td><td>0.012006150861982732</td><td>0.008986950271338471</td><td>2775</td><td>1.0003708102100584</td><td>0.9253913925579329</td><td>0.01587640316376797</td><td>0.011945629668644334</td><td>2775</td><td>0.9999629444372514</td><td>0.6012130410382595</td><td>0.020954229679142105</td><td>0.015287445913223813</td><td>2775</td><td>0.999952382768961</td><td>0.5847551343491033</td><td>0.034596802984993714</td><td>0.025068505153244595</td><td>2775</td><td>0.271742948888724</td><td>0.385786571762731</td><td>0.09041192951455833</td><td>0.06486283568862884</td><td>2775</td><td>0.000870765250533563</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0042335255686836125</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.30297438438353747</td><td>0.0729137126199859</td><td>0.17875572974377257</td><td>0.1425808222110095</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.2211925775581921</td><td>-0.10563051622940384</td><td>0.4136296577937412</td><td>0.3299245935603866</td><td>2775</td><td>1.0000337085333644</td><td>0.33738668400013666</td><td>0.004950199713314884</td><td>0.003915120681098042</td><td>2775</td><td>1.0001181069105798</td><td>0.4548665953094292</td><td>0.0043750033335366945</td><td>0.0034114654722886342</td><td>2775</td><td>1.001699616190192</td><td>0.4504944699708305</td><td>0.007085518684495233</td><td>0.005398401794143544</td><td>2775</td><td>1.0000088989496112</td><td>0.32547592596442326</td><td>0.005407843553604075</td><td>0.004276370382439811</td><td>2775</td><td>1.0004391319019352</td><td>0.5330539495518211</td><td>0.004904124090599388</td><td>0.0038212765386505553</td><td>2775</td><td>0.9675655946156906</td><td>0.6715857097916574</td><td>0.010553795880270628</td><td>0.00794324809030287</td><td>2775</td><td>0.9587468093273036</td><td>0.5833624760823622</td><td>0.019415353864716576</td><td>0.014090356633500783</td><td>2775</td><td>0.010634676241646013</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2775</td><td>0.5946532185930513</td><td>0.14378560988350406</td><td>0.08065630650619657</td><td>0.06433176255255493</td><td>2775</td><td>0.9991700000926202</td><td>0.43613237675563177</td><td>0.007582746197806663</td><td>0.0058824222012783854</td><td>2775</td><td>0.9993484777878848</td><td>0.5972217145015718</td><td>0.022166001353858905</td><td>0.016079926523872485</td><td>--</td><td>--</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td></tr>
<tr><td>gto-wide-uds13-v4_g235h-f170lp_1215_1951.spec.fits</td><td>1951</td><td>34.35065901</td><td>-5.14988767</td><td>G235H</td><td>F170LP</td><td>802.389</td><td>4</td><td>jw01215013001_04101_00001_nrs2_f170lp_g235h_raw.70.1215_1951.fits</td><td>jw01215013001_01_msa.fits</td><td>205</td><td>1</td><td>1</td><td>70</td><td>gto-wide-uds13-v4</td><td>2243</td><td>1</td><td>1.66</td><td>2.5689142</td><td>2.0963542</td><td>-0.4861431</td><td>-0.7656741</td><td>1.2593989</td><td>0.49343532</td><td>0.8224826</td><td>1.5858558</td><td>1.5304534</td><td>2.459035</td><td>2.1690035</td><td>1</td><td>1367</td><td>2048</td><td>40</td><td>0.0</td><td>253.84996</td><td>0.0</td><td>-0.001</td><td>0.4917679</td><td>1738073094.4070385</td><td>0.9.5.dev2+g80b81b4</td><td>1604.778</td><td>2913.6748</td><td>2243</td><td>2811.6072</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>139.03279</td><td>84.556435</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>153.81612</td><td>61.984585</td><td>--</td><td>--</td><td>--</td><td>--</td><td>4.0369225</td><td>78.60983</td><td>45.681705</td><td>80.60967</td><td>-50.989677</td><td>87.71492</td><td>73.9701</td><td>77.34231</td><td>--</td><td>--</td><td>--</td><td>--</td><td>853.96075</td><td>--</td><td>--</td><td>94.13828</td><td>--</td><td>--</td><td>--</td><td>-30.710531</td><td>61.72949</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-1.0793935</td><td>2.6578977</td><td>16.855896</td><td>6.094411</td><td>1.0531783</td><td>5.0059447</td><td>1.0905654</td><td>3.1887467</td><td>1.2597305</td><td>4.4599857</td><td>2.4125624</td><td>-0.024661088</td><td>12.698964</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>3.1934314</td><td>-15.388187</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>4.417971</td><td>9.601779</td><td>2.1934223</td><td>8.963685</td><td>1.6506367</td><td>7.166141</td><td>1.3367475</td><td>8.372035</td><td>1.2125107</td><td>4.2663774</td><td>1.2317595</td><td>4.6491623</td><td>1.1557022</td><td>3.8828688</td><td>1.0895466</td><td>4.6232686</td><td>--</td><td>--</td><td>47.9303</td><td>61.00501</td><td>-43.66452</td><td>73.04057</td><td>-52.864967</td><td>69.1943</td><td>49.73135</td><td>74.62461</td><td>-10.002572</td><td>82.228905</td><td>-74.391235</td><td>64.71364</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>0.008058175</td><td>-0.11264437</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>27.334742</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>35.321674</td><td>--</td><td>--</td><td>0.9015683</td><td>10.652017</td><td>-5.7512264</td><td>9.181498</td><td>--</td><td>--</td><td>--</td><td>154.39067</td><td>--</td><td>--</td><td>--</td><td>-7.458391</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>10.362592</td><td>-9.0206</td><td>-10.356026</td><td>11.604869</td><td>-2.242879</td><td>-16.51436</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>9.1</td><td>1737732200.0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>True</td><td>172449</td><td>4.6228543</td><td>G</td><td>4.621582</td><td>4.6228543</td><td>1.85</td><td>5.58</td><td>0.07257426</td><td>primer-uds-north-grizli-v7.2-fix_phot.fits</td><td>39787</td><td>23.86</td><td>0.2917665994332862</td><td>0.0074583520942602035</td><td>0.375822323338598</td><td>0.007474258631804441</td><td>0.4462115844556865</td><td>0.006440427649332001</td><td>0.5739798944677847</td><td>0.0055131230600766225</td><td>0.8435675923509218</td><td>0.004741583591371624</td><td>1.0094882735221247</td><td>0.0047143753686044055</td><td>0.8893053372138517</td><td>0.007319798398806998</td><td>0.9324802470703117</td><td>0.006405565944800626</td><td>1.7697781011450084</td><td>32809883821.644165</td><td>0.50983775</td><td>0.8515203</td><td>1.7189896</td><td>4.3906884</td><td>1693531123.1206756</td><td>2439001724.140659</td><td>491718980.0611007</td><td>3</td><td>4.62327</td><td>Auto</td><td>Redshift matches gto-wide-uds13-v3_g395h-f290lp_1215_1951 z=4.6200</td><td>4.623268549909802</td><td>0.7094566388815146</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.08369159014504489</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.00013475212131107387</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>7.249783264163463e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>3.2292668859647866e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.028256245773143007</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>1.0330607810946189</td><td>0.751829671429764</td><td>0.04973013977286707</td><td>0.035054140773913674</td><td>2243</td><td>0.9524084506838898</td><td>0.6207777286405767</td><td>0.0736573840182249</td><td>0.051825351649700924</td><td>2243</td><td>0.9999932511778588</td><td>0.8908527089506119</td><td>0.07184763333844787</td><td>0.05074208178806568</td><td>2243</td><td>0.23310679085591418</td><td>0.8177757649943135</td><td>0.08566965046817829</td><td>0.06086890897960933</td><td>2243</td><td>5.297289023649329e-06</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>8.489538935327642e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.8606606796384908</td><td>0.8178803577738383</td><td>0.08737503479687701</td><td>0.062074657324958316</td><td>2243</td><td>8.430932664970874e-06</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>6.407891996424609e-06</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>5.218707652222712e-06</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>2.556004809596254e-06</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>4.739559277072582e-06</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>5.993161422598339e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.00014867000081443158</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0013584849835228</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.029087078393880368</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>1.0046545627105983</td><td>0.7927240292799647</td><td>0.04908729006152204</td><td>0.03463403896219283</td><td>2243</td><td>0.7380643184262548</td><td>0.8502884964905775</td><td>0.0557017349117636</td><td>0.039493381601504375</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>1.0047200185225604</td><td>0.9022653741644692</td><td>0.05394973630312748</td><td>0.03805450115900114</td><td>2243</td><td>0.397884286922348</td><td>0.8632327999257797</td><td>0.05918354837837783</td><td>0.04200758750271939</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2243</td><td>0.31974527018089305</td><td>0.307244370316466</td><td>0.08745301357320409</td><td>0.06138968979032876</td><td>2243</td><td>0.6803023023793408</td><td>0.8133101267723994</td><td>0.09038907933801991</td><td>0.06421638157582743</td><td>2243</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>--</td><td>--</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td></tr>
<tr><td>gto-wide-uds13-v4_g395h-f290lp_1215_1951.spec.fits</td><td>1951</td><td>34.35065901</td><td>-5.14988767</td><td>G395H</td><td>F290LP</td><td>875.333</td><td>4</td><td>jw01215013001_07101_00001_nrs1_f290lp_g395h_raw.70.1215_1951.fits</td><td>jw01215013001_01_msa.fits</td><td>207</td><td>1</td><td>1</td><td>70</td><td>gto-wide-uds13-v4</td><td>2181</td><td>1</td><td>2.83</td><td>4.333257</td><td>3.0323372</td><td>-0.78633463</td><td>-15.713539</td><td>12.172805</td><td>0.023815606</td><td>0.3733426</td><td>18.183922</td><td>0.86755025</td><td>16.770237</td><td>29.427864</td><td>1613</td><td>1366</td><td>436</td><td>24</td><td>0.0</td><td>253.8499</td><td>0.0</td><td>0.0009999998</td><td>0.4917679</td><td>1738073098.9230382</td><td>0.9.5.dev2+g80b81b4</td><td>1750.666</td><td>2725.7173</td><td>2181</td><td>2691.6755</td><td>23.426165</td><td>412.583</td><td>19.938076</td><td>307.09857</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>1451.3488</td><td>428.4478</td><td>99.84564</td><td>273.67517</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>845.74225</td><td>630.42847</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-14.739792</td><td>16.296173</td><td>12.941133</td><td>1.0238339</td><td>3.397932</td><td>-3.8911495</td><td>3.7097752</td><td>7.1149216</td><td>3.9599311</td><td>-7.7766714</td><td>6.362927</td><td>37.82434</td><td>21.133274</td><td>-1564.3295</td><td>707.8916</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>20.102354</td><td>9.97284</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>16.226713</td><td>-5.647535</td><td>6.8985815</td><td>19.841732</td><td>5.6790743</td><td>-17.208584</td><td>4.4015408</td><td>12.006447</td><td>3.8504024</td><td>-5.2901826</td><td>3.5769703</td><td>10.483284</td><td>3.5806997</td><td>-0.044838645</td><td>3.3536315</td><td>4.5170674</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-6.600751</td><td>413.02917</td><td>35.67981</td><td>398.38538</td><td>--</td><td>--</td><td>261.49884</td><td>355.15863</td><td>129.73485</td><td>455.60483</td><td>-77.98808</td><td>304.73105</td><td>1188.4515</td><td>320.5895</td><td>-734.2784</td><td>440.50098</td><td>-461.14597</td><td>403.66617</td><td>-347.5903</td><td>561.14636</td><td>-0.05869624</td><td>-0.35027233</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-53.510654</td><td>7.888203</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>486.24625</td><td>435.344</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>213.96024</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-1.9749123</td><td>5.7209954</td><td>94.409485</td><td>31.447783</td><td>70.47738</td><td>-1292.1211</td><td>-123.25613</td><td>-80.68548</td><td>-96.06516</td><td>3.7</td><td>1737732200.0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>False</td><td>172449</td><td>4.6228543</td><td>G</td><td>4.621582</td><td>4.6228543</td><td>1.85</td><td>5.58</td><td>0.07257426</td><td>primer-uds-north-grizli-v7.2-fix_phot.fits</td><td>39787</td><td>23.86</td><td>0.2917665994332862</td><td>0.0074583520942602035</td><td>0.375822323338598</td><td>0.007474258631804441</td><td>0.4462115844556865</td><td>0.006440427649332001</td><td>0.5739798944677847</td><td>0.0055131230600766225</td><td>0.8435675923509218</td><td>0.004741583591371624</td><td>1.0094882735221247</td><td>0.0047143753686044055</td><td>0.8893053372138517</td><td>0.007319798398806998</td><td>0.9324802470703117</td><td>0.006405565944800626</td><td>1.7697781011450084</td><td>32809883821.644165</td><td>0.50983775</td><td>0.8515203</td><td>1.7189896</td><td>4.3906884</td><td>1693531123.1206756</td><td>2439001724.140659</td><td>491718980.0611007</td><td>--</td><td>--</td><td>--</td><td>--</td><td>4.517067232777931</td><td>0.5648607884785078</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.37837280603318735</td><td>0.3007337887735032</td><td>0.7444602012873731</td><td>0.4907047701126011</td><td>2181</td><td>0.9999772581563087</td><td>1.084959056058827</td><td>0.5379013681410073</td><td>0.32585015996468586</td><td>2181</td><td>0.4657190608823929</td><td>0.31645612242976445</td><td>0.9023031161466659</td><td>0.5029371099616546</td><td>2181</td><td>0.00010345898399421568</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.9713751020322826</td><td>0.45741863229009794</td><td>0.6887062354330475</td><td>0.4520323682998193</td><td>2181</td><td>0.9999788368443016</td><td>0.6306389182611222</td><td>0.8378392845863539</td><td>0.5215868519557816</td><td>2181</td><td>0.9999177797792165</td><td>1.5695825550910243</td><td>0.7339878408469604</td><td>0.4392704336981855</td><td>2181</td><td>0.9899288507048044</td><td>0.3378114355915089</td><td>0.8727410400891275</td><td>0.4888449496559451</td><td>2181</td><td>0.7262410592787684</td><td>0.7287832570032731</td><td>1.6251451026126238</td><td>0.8896363318577546</td><td>2181</td><td>0.0002046558169208894</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>8.095252757928491e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.025478101225164525</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.8291742799690571</td><td>0.46436990342848333</td><td>0.585386872116059</td><td>0.38255718808494726</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.15580905088338265</td><td>-0.12238282400133234</td><td>1.1890295304975842</td><td>0.795285131134417</td><td>2181</td><td>1.000795535675803</td><td>0.9472319776531377</td><td>0.5981600454935136</td><td>0.37015996906099646</td><td>2181</td><td>0.788454047968125</td><td>0.4860997689158019</td><td>0.7950771131455208</td><td>0.4469232974920383</td><td>2181</td><td>3.0335519041963066e-05</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>2181</td><td>0.8620101263997639</td><td>0.32700304883301073</td><td>0.8894654801456295</td><td>0.4967532214376828</td><td>--</td><td>--</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td></tr>
<tr><td>gto-wide-uds13-v4_prism-clear_1215_1951.spec.fits</td><td>1951</td><td>34.35065901</td><td>-5.14988767</td><td>PRISM</td><td>CLEAR</td><td>802.389</td><td>3</td><td>jw01215013001_03101_00002_nrs2_clear_prism_raw.70.1215_1951.fits</td><td>jw01215013001_01_msa.fits</td><td>1</td><td>1</td><td>1</td><td>70</td><td>gto-wide-uds13-v4</td><td>468</td><td>1</td><td>0.54912597</td><td>5.5018334</td><td>3.6847322</td><td>2.3243139</td><td>0.25463933</td><td>0.02617235</td><td>9.302495</td><td>0.52588886</td><td>0.056728948</td><td>15.833174</td><td>0.81377536</td><td>0.24621214</td><td>1</td><td>1359</td><td>506</td><td>28</td><td>0.0</td><td>253.85</td><td>0.0</td><td>0.001</td><td>0.4917679</td><td>1738073090.4590383</td><td>0.9.5.dev2+g80b81b4</td><td>2407.167</td><td>5617.831</td><td>468</td><td>613.4004</td><td>48.812813</td><td>22.620071</td><td>-2.438987</td><td>20.292538</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>560.37775</td><td>46.52388</td><td>71.51085</td><td>62.164665</td><td>--</td><td>--</td><td>-209.0797</td><td>133.7496</td><td>80.514854</td><td>28.133654</td><td>40.78571</td><td>23.218676</td><td>60.545902</td><td>23.915543</td><td>96.50616</td><td>43.993908</td><td>291.39352</td><td>75.85304</td><td>-716.07837</td><td>280.87146</td><td>57.39623</td><td>118.88307</td><td>514.75586</td><td>138.25935</td><td>124.91836</td><td>69.47591</td><td>16.877195</td><td>89.80219</td><td>-47.70294</td><td>94.665474</td><td>47.62188</td><td>198.28189</td><td>99.01638</td><td>32.63919</td><td>733.29956</td><td>52.67196</td><td>21.678513</td><td>83.931694</td><td>--</td><td>202.1944</td><td>241.93048</td><td>-169.24973</td><td>72.94585</td><td>932.3925</td><td>51.213474</td><td>2339.1604</td><td>70.73323</td><td>--</td><td>-12.027637</td><td>30.294546</td><td>260.65622</td><td>45.92269</td><td>-66.22304</td><td>32.629578</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>241.58337</td><td>27.795877</td><td>126.88221</td><td>33.298237</td><td>228.29633</td><td>42.907158</td><td>40.989212</td><td>24.233473</td><td>13.529544</td><td>1.5309826</td><td>0.066841386</td><td>1.214747</td><td>0.065447986</td><td>1.278438</td><td>0.06856148</td><td>1.1027563</td><td>0.070816785</td><td>1.0249417</td><td>0.063015215</td><td>0.89060324</td><td>0.06667906</td><td>0.86389846</td><td>0.07108439</td><td>0.651814</td><td>0.08272743</td><td>0.89211535</td><td>0.098206654</td><td>0.799955</td><td>0.1357211</td><td>7.2655287</td><td>22.44103</td><td>0.5588701</td><td>0.20240332</td><td>0.870177</td><td>0.2691064</td><td>0.25699463</td><td>0.49232814</td><td>2.700355</td><td>14.098136</td><td>0.95429015</td><td>10.180353</td><td>0.3941978</td><td>5.217168</td><td>0.22023936</td><td>3.3910584</td><td>0.15795249</td><td>2.8573809</td><td>0.12847427</td><td>2.1295457</td><td>0.094936535</td><td>1.6646644</td><td>0.06834415</td><td>4.621582</td><td>-649.9793</td><td>196.06087</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-323.86383</td><td>244.54553</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>-0.020892859</td><td>-0.019805139</td><td>164.59029</td><td>193.0386</td><td>363.44467</td><td>219.52042</td><td>--</td><td>--</td><td>--</td><td>--</td><td>43.720543</td><td>-2.5788078</td><td>--</td><td>--</td><td>--</td><td>--</td><td>17.805237</td><td>-53.11091</td><td>2274.049</td><td>278.24475</td><td>25.7951</td><td>--</td><td>-70.51571</td><td>55.215572</td><td>35.792576</td><td>80.42899</td><td>-28.525156</td><td>44.31549</td><td>115.00771</td><td>-52.42033</td><td>12.157452</td><td>172.58456</td><td>43.14509</td><td>4.735929</td><td>-13.835131</td><td>4.564733</td><td>28.052313</td><td>77.97484</td><td>235.53954</td><td>49.396652</td><td>--</td><td>18.168468</td><td>-67.426506</td><td>482.79144</td><td>1235.6241</td><td>-14.254797</td><td>377.87656</td><td>-86.09008</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>195.16728</td><td>151.96198</td><td>334.70682</td><td>2837.5889</td><td>58.07976</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>48.9</td><td>1737732200.0</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>--</td><td>True</td><td>172449</td><td>4.6228543</td><td>G</td><td>4.621582</td><td>4.6228543</td><td>1.85</td><td>5.58</td><td>0.07257426</td><td>primer-uds-north-grizli-v7.2-fix_phot.fits</td><td>39787</td><td>23.86</td><td>0.2917665994332862</td><td>0.0074583520942602035</td><td>0.375822323338598</td><td>0.007474258631804441</td><td>0.4462115844556865</td><td>0.006440427649332001</td><td>0.5739798944677847</td><td>0.0055131230600766225</td><td>0.8435675923509218</td><td>0.004741583591371624</td><td>1.0094882735221247</td><td>0.0047143753686044055</td><td>0.8893053372138517</td><td>0.007319798398806998</td><td>0.9324802470703117</td><td>0.006405565944800626</td><td>1.7697781011450084</td><td>32809883821.644165</td><td>0.50983775</td><td>0.8515203</td><td>1.7189896</td><td>4.3906884</td><td>1693531123.1206756</td><td>2439001724.140659</td><td>491718980.0611007</td><td>3</td><td>4.62158</td><td>Auto</td><td>Redshift matches gto-wide-uds13-v3_g395h-f290lp_1215_1951 z=4.6200</td><td>4.621581822366623</td><td>0.9710891829132017</td><td>468</td><td>0.9993118773223624</td><td>0.29734528736854304</td><td>0.005072510088040735</td><td>0.005767177676298873</td><td>468</td><td>1.0049920554790184</td><td>0.39358077725769736</td><td>0.006754919246597596</td><td>0.007532034658250185</td><td>468</td><td>0.9994121589090459</td><td>0.2105169070779525</td><td>0.005740663780735214</td><td>0.006500276615422723</td><td>468</td><td>1.0048331387204024</td><td>0.3142774578677898</td><td>0.0056972625518462</td><td>0.006475589632160145</td><td>468</td><td>1.0057802954242325</td><td>0.3633855175643899</td><td>0.005552140260213317</td><td>0.0063232330890943475</td><td>468</td><td>0.9969378740446078</td><td>0.390086461267687</td><td>0.006031948428263683</td><td>0.006740462634462128</td><td>468</td><td>0.9995545389631847</td><td>0.47428699929668094</td><td>0.006087252864125372</td><td>0.006644708782519558</td><td>468</td><td>0.9949583358463919</td><td>0.4221695478639817</td><td>0.008193361034636096</td><td>0.008954026097921097</td><td>468</td><td>0.9966398915013757</td><td>0.5330687735195239</td><td>0.00920935617242841</td><td>0.010074424705055462</td><td>468</td><td>1.000135743102705</td><td>0.6585727186306961</td><td>0.00540349388040512</td><td>0.005876314991454699</td><td>468</td><td>1.0001377456066418</td><td>0.7394149423240386</td><td>0.006323697221645326</td><td>0.0065784364741576125</td><td>468</td><td>1.000013567062085</td><td>0.6166311528474346</td><td>0.008695988683221448</td><td>0.008120834396306063</td><td>468</td><td>0.9973999343526664</td><td>0.5123215054081025</td><td>0.009529315724051777</td><td>0.010162216289208869</td><td>468</td><td>0.9998409327402623</td><td>0.5626509249823465</td><td>0.007773287358672584</td><td>0.008041947249691669</td><td>468</td><td>0.9995329666665248</td><td>0.5396141362524208</td><td>0.008187183943740751</td><td>0.008220709080628089</td><td>468</td><td>0.9999658710844571</td><td>0.9343532785573141</td><td>0.009678591326381328</td><td>0.010472675567219238</td><td>468</td><td>1.0000143039433227</td><td>0.6198705997379221</td><td>0.010520714370935278</td><td>0.010078224493847163</td><td>468</td><td>0.9997544208857447</td><td>0.6046318093271135</td><td>0.016583968030603233</td><td>0.015668615213923796</td><td>468</td><td>1.0004403138230038</td><td>0.6104681852342965</td><td>0.020620481299690376</td><td>0.01906515776929085</td><td>468</td><td>0.9997586216471691</td><td>0.6181443627182708</td><td>0.02107673853011141</td><td>0.019261352578809964</td><td>468</td><td>1.0005685988794546</td><td>0.3069343338892747</td><td>0.005583251896278126</td><td>0.006349944821663527</td><td>468</td><td>1.0003104619770644</td><td>0.3761750772827621</td><td>0.004312906982944125</td><td>0.004881883975885983</td><td>468</td><td>0.9904131708376346</td><td>0.31802241951276733</td><td>0.006028062674911858</td><td>0.006853123554938171</td><td>468</td><td>1.0107784320042819</td><td>0.389690293439562</td><td>0.008403419750412264</td><td>0.009342099415807005</td><td>468</td><td>1.0065232768365464</td><td>0.29651259700246846</td><td>0.006942986285491834</td><td>0.007903390037513149</td><td>468</td><td>0.9847564979575222</td><td>0.32320605184509554</td><td>0.008470150253087333</td><td>0.009614490334158416</td><td>468</td><td>1.0157188080544226</td><td>0.35958587157221905</td><td>0.00870528122208533</td><td>0.009880207569668304</td><td>468</td><td>1.0088670429538373</td><td>0.3976870900143664</td><td>0.010650006076162495</td><td>0.011869349833618707</td><td>468</td><td>0.9996170106520132</td><td>0.490647426381474</td><td>0.006174141010544129</td><td>0.006749864291928956</td><td>468</td><td>1.000184752460022</td><td>0.5686809441913387</td><td>0.005280487501663225</td><td>0.005684499640823398</td><td>468</td><td>1.0001471164580011</td><td>0.617824119776292</td><td>0.005899318910584339</td><td>0.00616102326630729</td><td>468</td><td>1.0001279166565336</td><td>0.4770255075760639</td><td>0.0066422708680174735</td><td>0.00725540569775386</td><td>468</td><td>0.9999969865492299</td><td>0.6548236950365218</td><td>0.005124902270081213</td><td>0.005617270097245955</td><td>468</td><td>0.9999998515125955</td><td>0.7575954360860535</td><td>0.006838287497065963</td><td>0.007237138306888876</td><td>468</td><td>0.9997355434741737</td><td>0.6194714287917443</td><td>0.009074522727257303</td><td>0.008616895171326298</td><td>468</td><td>0.9214708571648356</td><td>0.668345653523944</td><td>0.02038897155485026</td><td>0.01830167340888231</td><td>468</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>468</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>468</td><td>0.0</td><td>0.0</td><td>-1.0</td><td>-1.0</td><td>468</td><td>1.027102687446468</td><td>0.3910516613690073</td><td>0.007945509661014401</td><td>0.008788183019400268</td><td>468</td><td>0.9984309746369571</td><td>0.5230435541267343</td><td>0.00887556980792251</td><td>0.009462919431837948</td><td>468</td><td>1.0043779357206608</td><td>0.6176813660935505</td><td>0.010698828562773089</td><td>0.010147776185419594</td><td>-1.4565206479365085</td><td>0.3061252990650476</td><td>44</td><td>0.140362119861813</td><td>0.2567145919520727</td><td>1.195405434175183</td><td>15.0</td><td>18.563167366575303</td><td>5.144609137022997</td><td>0.0021474377023419544</td><td>-0.0001561310838130919</td><td>-0.00015613108381309188</td><td>1.803142058546427e-05</td></tr>
</table></div>




```python

#  see the description in the https://dawn-cph.github.io/dja/blog/2025/05/01/nirspec-merged-table-v4/
#  
RGB_URL = "https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord={ra}%2C{dec}"
msa['metafile'] = [m.split('_')[0] for m in msa['msamet']]
SLIT_URL = "https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord={ra}%2C{dec}&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile={metafile}"
FITS_URL = "https://s3.amazonaws.com/msaexp-nirspec/extractions/{root}/{file}"

msa['Thumb'] = [
    "<img src=\"{0}\" height=200px>".format(
        RGB_URL.format(**row['ra','dec'])
    )
    for row in msa
]

msa['Slit_Thumb'] = [
    "<img src=\"{0}\" height=200px>".format(
        SLIT_URL.format(**row['ra','dec','metafile'])
    )
    for row in msa
]

msa['Spectrum_fnu'] = [
    "<img src=\"{0}\" height=200px>".format(
        FITS_URL.format(**row['root','file']).replace('.spec.fits', '.fnu.png')
    )
    for row in msa
]

msa['Spectrum_flam'] = [
    "<img src=\"{0}\" height=200px>".format(
        FITS_URL.format(**row['root','file']).replace('.spec.fits', '.flam.png')
    )
    for row in msa
]

```


```python
df = msa['root','file','z_best','phot_mass','eqw_ha_nii','Thumb','Slit_Thumb','Spectrum_fnu', 'Spectrum_flam'].to_pandas()

display(Markdown(df.to_markdown()))
```


|    | root              | file                                               |   z_best |   phot_mass |   eqw_ha_nii | Thumb                                                                                                                                                                                                        | Slit_Thumb                                                                                                                                                                                                                                                 | Spectrum_fnu                                                                                                                                    | Spectrum_flam                                                                                                                                    |
|---:|:------------------|:---------------------------------------------------|---------:|------------:|-------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | excels-uds01-v4   | excels-uds01-v4_g235m-f170lp_3543_109269.spec.fits |  4.62285 | 3.28099e+10 |       nan    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35062413%2C-5.14987821" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35062413%2C-5.14987821&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw03543001001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/excels-uds01-v4/excels-uds01-v4_g235m-f170lp_3543_109269.fnu.png" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/excels-uds01-v4/excels-uds01-v4_g235m-f170lp_3543_109269.flam.png" height=200px>   |
|  1 | gto-wide-uds13-v4 | gto-wide-uds13-v4_g235h-f170lp_1215_1951.spec.fits |  4.62285 | 3.28099e+10 |       nan    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35065901%2C-5.14988767" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35065901%2C-5.14988767&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01215013001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_g235h-f170lp_1215_1951.fnu.png" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_g235h-f170lp_1215_1951.flam.png" height=200px> |
|  2 | gto-wide-uds13-v4 | gto-wide-uds13-v4_g395h-f290lp_1215_1951.spec.fits |  4.62285 | 3.28099e+10 |       nan    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35065901%2C-5.14988767" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35065901%2C-5.14988767&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01215013001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_g395h-f290lp_1215_1951.fnu.png" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_g395h-f290lp_1215_1951.flam.png" height=200px> |
|  3 | gto-wide-uds13-v4 | gto-wide-uds13-v4_prism-clear_1215_1951.spec.fits  |  4.62285 | 3.28099e+10 |      2274.05 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35065901%2C-5.14988767" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.35065901%2C-5.14988767&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01215013001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_prism-clear_1215_1951.fnu.png" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_prism-clear_1215_1951.flam.png" height=200px>  |



```python
# Reading the spectrum

for i in range(len(df)):
    spec_file = df['file'][i]
    row = msa[msa['file'] == spec_file][0]
    spec = msaexp.spectrum.SpectrumSampler(FITS_URL.format(**row))

    ## 
    con_mask = spec['full_err']==0 
    con_mask |= spec['full_err']> spec['flux']

    galaxy_masked = np.ma.masked_where(con_mask, spec['flux'])
    plt.plot(spec['wave'], galaxy_masked,
         label="{file}\nz={z_best:.3f}".format(**row), alpha=0.5)


plt.xlim([0.8,6])
plt.ylim(top=galaxy_masked.max()*2)
plt.semilogx()
plt.legend(fontsize=7, ncol=1)
```




    <matplotlib.legend.Legend at 0x3117895e0>




    
![png]({{ site.baseurl }}/assets/post_files/2025-11-20-ecogal-dja-showcase_files/ecogal-dja-showcase_61_1.png)
    

