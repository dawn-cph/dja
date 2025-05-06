---
layout: post
title:   NIRSpec Merged Table
date:   2025-05-01 10:11:28 +0200
categories: spectroscopy
tags: nirspec release catalog
author: Gabriel Brammer
showOnHighlights: true
---
{% include components/tags.html %}
(This page is auto-generated from the Jupyter notebook [nirspec-merged-table-v4.ipynb]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4.ipynb).)

Demo of full merged table of NIRSpec spectra reduced with [msaexp](http://github.com/gbrammer/msaexp).  The merged columns are taken from the database tables

- `nirspec_extractions` - Basic spectrum parameters (grating, mask, exposure time, etc.)
- `nirspec_redshifts` - Redshift fit results, emission line fluxes
- `nirspec_redshifts_manual` - Grades and comments from visual inspection
- `nirspec_integrated` - Observed- and rest-frame filters integrated through the spectra at the derived redshift
- `grizli_photometry` - Photometry and some eazy outputs of the nearest counterpart in the DJA/grizli photometric catalogs

The public spectra are shown in a large overview table at [public_prelim_v4.2.html](https://s3.amazonaws.com/msaexp-nirspec/extractions/public_prelim_v4.2.html).

<a href="https://colab.research.google.com/github/dawn-cph/dja/blob/master/assets/post_files/2025-05-01-nirspec-merged-table-v4.ipynb"> <img src="https://colab.research.google.com/assets/colab-badge.svg"> </a>



```python
# Install dependencies, e.g., on Google Colab
try:
    import msaexp

except ImportError:

    ! pip install msaexp
    ! pip install git+https://github.com/karllark/dust_attenuation.git
    
    import eazy
    eazy.fetch_eazy_photoz()
```


```python
%matplotlib inline

import os
import yaml

import numpy as np
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from scipy.spatial import cKDTree

import astropy.io.fits as pyfits
from astropy.utils.data import download_file
from astropy.cosmology import WMAP9
import astropy.units as u

import grizli
import grizli.catalog
from grizli import utils

import eazy
import msaexp

print(f'grizli version: {grizli.__version__}')
print(f'eazy-py version: {eazy.__version__}')
print(f'msaexp version: {msaexp.__version__}')
```

    grizli version: 1.12.12.dev5+g5896d62.d20250426
    eazy-py version: 0.8.5
    msaexp version: 0.9.8.dev3+ge0e3f39.d20250429


## Read the table


```python
# Full table
table_url = "https://s3.amazonaws.com/msaexp-nirspec/extractions/dja_msaexp_emission_lines_v4.0.csv.gz"
tab = utils.read_catalog(download_file(table_url, cache=True), format='csv')
```


```python
# Column descriptions
columns_url = "https://s3.amazonaws.com/msaexp-nirspec/extractions/dja_msaexp_emission_lines_v4.0.columns.csv"
tab_columns = utils.read_catalog(download_file(columns_url, cache=True), format='csv')

# Set column metadata
for row in tab_columns:
    c = row['column']
    if row['unit'] != '--':
        tab[c].unit = row['unit']
    if row['format'] != '--':
        tab[c].format = row['format']
    if row['description'] != '--':
        tab[c].description = row['description']

tab.info()
```

    <GTable length=52181>
            name         dtype   unit  format                                       description                                           class     n_bad
    ------------------- ------- ------ ------ ---------------------------------------------------------------------------------------- ------------ -----
                   file   str57                                                                                           DJA filename       Column     0
                  srcid   int64                                                                                Source ID from APT plan       Column     0
                     ra float64    deg    .8f                                                                         RA from APT plan       Column     0
                    dec float64    deg    .8f                                                                        Dec from APT plan       Column     0
                grating    str5                                                                                        NIRSpec grating       Column     0
                 filter    str6                                                                                        Blocking filter       Column     0
               effexptm float64                                                               Effective exposure time of each exposure       Column     0
                 nfiles   int64                                                             Number of files combined in final spectrum       Column     0
                dataset   str72                                                                             Filename of first exposure       Column     0
                 msamet   str25                                                                                      MSA metadata file       Column     0
                  msaid   int64                                                                                        MSA metadata ID       Column     0
                 msacnf   int64                                                                                    MSA metadata config       Column     0
                  dithn   int64                                                                                          Dither number       Column     0
                 slitid   int64                                                                                       MSA plan slit ID       Column     0
                   root   str24                                                                            DJA program + mask rootname       Column     0
                   npix   int64                                                                    Number of pixels in the 2D spectrum       Column     0
                   ndet   int64                                                             Number of detectors contributing to output       Column     0
                   wmin float64 micron                                                     Minimum wavelength of the combined spectrum       Column     0
                   wmax float64 micron                                                     Maximum wavelength of the combined spectrum       Column     0
                 wmaxsn float64 micron                                                           Wavelength of maximum signal to noise       Column     0
                   sn10 float64                                                                                     10th percentile SN       Column     0
                 flux10 float64                                                                                           Flux at sn10       Column     0
                  err10 float64                                                                                    Uncertainty at sn50       Column     0
                   sn50 float64                                                                                     50th percentile SN       Column     0
                 flux50 float64                                                                                           Flux at sn50       Column     0
                  err50 float64                                                                                    Uncertainty at sn90       Column     0
                   sn90 float64                                                                                     90th percentile SN       Column     0
                 flux90 float64                                                                                           Flux at sn90       Column     0
                  err90 float64                                                                                    Uncertainty at sn90       Column     0
                 xstart   int64                                                            Starting detector x coordinate of 2D cutout       Column     0
                 ystart   int64                                                            Starting detector y coordinate of 2D cutout       Column     0
                  xsize   int64                                                                                    x size of 2D cutout       Column     0
                  ysize   int64                                                                                    y size of 2D cutout       Column     0
                slit_pa float64                                                                            Estimated PA of the slitlet       Column     0
                  pa_v3 float64                                                                 Estimated PA of the spacecraft V3 axis       Column     0
                srcypix float64                                                              Location of the source in the 2D spectrum       Column     0
                profcen float64                                                         Profile offset relative to the expected center       Column     0
                profsig float64                                                           Derived profile width in pixels added to PSF       Column     0
                  ctime float64                                                                      UNIX time when file was generated       Column     0
                version   str29                                                                                    MSAEXP code version       Column     0
                exptime float64                                                                          Estimated total exposure time       Column     0
               contchi2 float64                                                                       Chi2 of the spline continuum fit       Column     0
                    dof   int64                                                      Total number of pixels in the redshift + line fit       Column     0
               fullchi2 float64                                                                  Chi2 of the full continuum + line fit       Column     0
        line_ariii_7138 float64                                                              Line flux of ariii_7138 1e-20 erg/s/cm2/A MaskedColumn 15150
    line_ariii_7138_err float64                                                                                                        MaskedColumn 15154
        line_ariii_7753 float64                                                              Line flux of ariii_7753 1e-20 erg/s/cm2/A MaskedColumn 16447
    line_ariii_7753_err float64                                                                                                        MaskedColumn 16448
               line_bra float64                                                                     Line flux of bra 1e-20 erg/s/cm2/A MaskedColumn 50121
           line_bra_err float64                                                                                                        MaskedColumn 50121
               line_brb float64                                                                     Line flux of brb 1e-20 erg/s/cm2/A MaskedColumn 45143
           line_brb_err float64                                                                                                        MaskedColumn 45143
               line_brd float64                                                                     Line flux of brd 1e-20 erg/s/cm2/A MaskedColumn 39919
           line_brd_err float64                                                                                                        MaskedColumn 39919
               line_brg float64                                                                     Line flux of brg 1e-20 erg/s/cm2/A MaskedColumn 42185
           line_brg_err float64                                                                                                        MaskedColumn 42185
                line_hb float64                                                                      Line flux of hb 1e-20 erg/s/cm2/A MaskedColumn 15758
            line_hb_err float64                                                                                                        MaskedColumn 15758
                line_hd float64                                                                      Line flux of hd 1e-20 erg/s/cm2/A MaskedColumn 19039
            line_hd_err float64                                                                                                        MaskedColumn 19039
          line_hei_1083 float64                                                                Line flux of hei_1083 1e-20 erg/s/cm2/A MaskedColumn 23917
      line_hei_1083_err float64                                                                                                        MaskedColumn 23919
          line_hei_3889 float64                                                                Line flux of hei_3889 1e-20 erg/s/cm2/A MaskedColumn 28197
      line_hei_3889_err float64                                                                                                        MaskedColumn 28199
          line_hei_5877 float64                                                                Line flux of hei_5877 1e-20 erg/s/cm2/A MaskedColumn 14136
      line_hei_5877_err float64                                                                                                        MaskedColumn 14136
          line_hei_7065 float64                                                                Line flux of hei_7065 1e-20 erg/s/cm2/A MaskedColumn 14970
      line_hei_7065_err float64                                                                                                        MaskedColumn 14974
          line_hei_8446 float64                                                                Line flux of hei_8446 1e-20 erg/s/cm2/A MaskedColumn 18135
      line_hei_8446_err float64                                                                                                        MaskedColumn 18135
         line_heii_4687 float64                                                               Line flux of heii_4687 1e-20 erg/s/cm2/A MaskedColumn 34207
     line_heii_4687_err float64                                                                                                        MaskedColumn 34207
                line_hg float64                                                                      Line flux of hg 1e-20 erg/s/cm2/A MaskedColumn 17895
            line_hg_err float64                                                                                                        MaskedColumn 17895
               line_lya float64                                                                     Line flux of lya 1e-20 erg/s/cm2/A MaskedColumn 42233
           line_lya_err float64                                                                                                        MaskedColumn 42233
              line_mgii float64                                                                    Line flux of mgii 1e-20 erg/s/cm2/A MaskedColumn 26145
          line_mgii_err float64                                                                                                        MaskedColumn 26145
        line_neiii_3867 float64                                                              Line flux of neiii_3867 1e-20 erg/s/cm2/A MaskedColumn 36500
    line_neiii_3867_err float64                                                                                                        MaskedColumn 36501
        line_neiii_3968 float64                                                              Line flux of neiii_3968 1e-20 erg/s/cm2/A MaskedColumn 19795
    line_neiii_3968_err float64                                                                                                        MaskedColumn 19796
          line_nev_3346 float64                                                                Line flux of nev_3346 1e-20 erg/s/cm2/A MaskedColumn 23094
      line_nev_3346_err float64                                                                                                        MaskedColumn 23094
         line_nevi_3426 float64                                                               Line flux of nevi_3426 1e-20 erg/s/cm2/A MaskedColumn 22671
     line_nevi_3426_err float64                                                                                                        MaskedColumn 22672
         line_niii_1750 float64                                                               Line flux of niii_1750 1e-20 erg/s/cm2/A MaskedColumn 34895
     line_niii_1750_err float64                                                                                                        MaskedColumn 34895
           line_oi_6302 float64                                                                 Line flux of oi_6302 1e-20 erg/s/cm2/A MaskedColumn 13908
       line_oi_6302_err float64                                                                                                        MaskedColumn 13908
               line_oii float64                                                                     Line flux of oii 1e-20 erg/s/cm2/A MaskedColumn 21033
          line_oii_7325 float64                                                                Line flux of oii_7325 1e-20 erg/s/cm2/A MaskedColumn 28002
      line_oii_7325_err float64                                                                                                        MaskedColumn 28003
           line_oii_err float64                                                                                                        MaskedColumn 21034
              line_oiii float64                                                 Line flux of combined OIII 4959+5007 1e-20 erg/s/cm2/A MaskedColumn 33972
         line_oiii_1663 float64                                                               Line flux of oiii_1663 1e-20 erg/s/cm2/A MaskedColumn 35844
     line_oiii_1663_err float64                                                                                                        MaskedColumn 35844
         line_oiii_4363 float64                                                               Line flux of oiii_4363 1e-20 erg/s/cm2/A MaskedColumn 35022
     line_oiii_4363_err float64                                                                                                        MaskedColumn 35022
         line_oiii_4959 float64                                                               Line flux of oiii_4959 1e-20 erg/s/cm2/A MaskedColumn 33702
     line_oiii_4959_err float64                                                                                                        MaskedColumn 33702
         line_oiii_5007 float64                                                               Line flux of oiii_5007 1e-20 erg/s/cm2/A MaskedColumn 33582
     line_oiii_5007_err float64                                                                                                        MaskedColumn 33582
          line_oiii_err float64                                                                                                        MaskedColumn 33972
              line_pa10 float64                                                                    Line flux of pa10 1e-20 erg/s/cm2/A MaskedColumn 19644
          line_pa10_err float64                                                                                                        MaskedColumn 19647
               line_pa8 float64                                                                     Line flux of pa8 1e-20 erg/s/cm2/A MaskedColumn 20954
           line_pa8_err float64                                                                                                        MaskedColumn 20955
               line_pa9 float64                                                                     Line flux of pa9 1e-20 erg/s/cm2/A MaskedColumn 20157
           line_pa9_err float64                                                                                                        MaskedColumn 20158
               line_paa float64                                                                     Line flux of paa 1e-20 erg/s/cm2/A MaskedColumn 38990
           line_paa_err float64                                                                                                        MaskedColumn 38990
               line_pab float64                                                                     Line flux of pab 1e-20 erg/s/cm2/A MaskedColumn 29296
           line_pab_err float64                                                                                                        MaskedColumn 29297
               line_pad float64                                                                     Line flux of pad 1e-20 erg/s/cm2/A MaskedColumn 22224
           line_pad_err float64                                                                                                        MaskedColumn 22226
               line_pag float64                                                                     Line flux of pag 1e-20 erg/s/cm2/A MaskedColumn 24212
           line_pag_err float64                                                                                                        MaskedColumn 24214
               line_pfb float64                                                                     Line flux of pfb 1e-20 erg/s/cm2/A MaskedColumn 51327
           line_pfb_err float64                                                                                                        MaskedColumn 51327
               line_pfd float64                                                                     Line flux of pfd 1e-20 erg/s/cm2/A MaskedColumn 48116
           line_pfd_err float64                                                                                                        MaskedColumn 48116
               line_pfe float64                                                                     Line flux of pfe 1e-20 erg/s/cm2/A MaskedColumn 47147
           line_pfe_err float64                                                                                                        MaskedColumn 47147
               line_pfg float64                                                                     Line flux of pfg 1e-20 erg/s/cm2/A MaskedColumn 49381
           line_pfg_err float64                                                                                                        MaskedColumn 49381
               line_sii float64                                                                     Line flux of sii 1e-20 erg/s/cm2/A MaskedColumn 27029
           line_sii_err float64                                                                                                        MaskedColumn 27034
         line_siii_9068 float64                                                               Line flux of siii_9068 1e-20 erg/s/cm2/A MaskedColumn 19788
     line_siii_9068_err float64                                                                                                        MaskedColumn 19791
         line_siii_9531 float64                                                               Line flux of siii_9531 1e-20 erg/s/cm2/A MaskedColumn 20920
     line_siii_9531_err float64                                                                                                        MaskedColumn 20922
                  spl_0 float64                                                                         Spline continuum coefficient 0       Column     0
              spl_0_err float64                                                                                                              Column     0
                  spl_1 float64                                                                         Spline continuum coefficient 1       Column     0
                 spl_10 float64                                                                        Spline continuum coefficient 10       Column     0
             spl_10_err float64                                                                                                              Column     0
                 spl_11 float64                                                                        Spline continuum coefficient 11       Column     0
             spl_11_err float64                                                                                                              Column     0
                 spl_12 float64                                                                        Spline continuum coefficient 12       Column     0
             spl_12_err float64                                                                                                              Column     0
                 spl_13 float64                                                                        Spline continuum coefficient 13       Column     0
             spl_13_err float64                                                                                                              Column     0
                 spl_14 float64                                                                        Spline continuum coefficient 14       Column     0
             spl_14_err float64                                                                                                              Column     0
                 spl_15 float64                                                                        Spline continuum coefficient 15       Column     0
             spl_15_err float64                                                                                                              Column     0
                 spl_16 float64                                                                        Spline continuum coefficient 16       Column     0
             spl_16_err float64                                                                                                              Column     0
                 spl_17 float64                                                                        Spline continuum coefficient 17       Column     0
             spl_17_err float64                                                                                                              Column     0
                 spl_18 float64                                                                        Spline continuum coefficient 18       Column     0
             spl_18_err float64                                                                                                              Column     0
                 spl_19 float64                                                                        Spline continuum coefficient 19       Column     0
             spl_19_err float64                                                                                                              Column     0
              spl_1_err float64                                                                                                              Column     0
                  spl_2 float64                                                                         Spline continuum coefficient 2       Column     0
                 spl_20 float64                                                                        Spline continuum coefficient 20       Column     0
             spl_20_err float64                                                                                                              Column     0
                 spl_21 float64                                                                        Spline continuum coefficient 21       Column     0
             spl_21_err float64                                                                                                              Column     0
                 spl_22 float64                                                                        Spline continuum coefficient 22       Column     0
             spl_22_err float64                                                                                                              Column     0
              spl_2_err float64                                                                                                              Column     0
                  spl_3 float64                                                                         Spline continuum coefficient 3       Column     0
              spl_3_err float64                                                                                                              Column     0
                  spl_4 float64                                                                         Spline continuum coefficient 4       Column     0
              spl_4_err float64                                                                                                              Column     0
                  spl_5 float64                                                                         Spline continuum coefficient 5       Column     0
              spl_5_err float64                                                                                                        MaskedColumn     1
                  spl_6 float64                                                                         Spline continuum coefficient 6       Column     0
              spl_6_err float64                                                                                                        MaskedColumn     1
                  spl_7 float64                                                                         Spline continuum coefficient 7       Column     0
              spl_7_err float64                                                                                                        MaskedColumn     5
                  spl_8 float64                                                                         Spline continuum coefficient 8       Column     0
              spl_8_err float64                                                                                                        MaskedColumn     1
                  spl_9 float64                                                                         Spline continuum coefficient 9       Column     0
              spl_9_err float64                                                                                                        MaskedColumn     2
                  zline float64                                                                     Redshift where the lines where fit       Column     0
          line_civ_1549 float64                                                                Line flux of civ_1549 1e-20 erg/s/cm2/A MaskedColumn 37413
      line_civ_1549_err float64                                                                                                        MaskedColumn 37413
               line_h10 float64                                                                     Line flux of h10 1e-20 erg/s/cm2/A MaskedColumn 44444
           line_h10_err float64                                                                                                        MaskedColumn 44444
               line_h11 float64                                                                     Line flux of h11 1e-20 erg/s/cm2/A MaskedColumn 44547
           line_h11_err float64                                                                                                        MaskedColumn 44547
               line_h12 float64                                                                     Line flux of h12 1e-20 erg/s/cm2/A MaskedColumn 44585
           line_h12_err float64                                                                                                        MaskedColumn 44585
                line_h7 float64                                                                      Line flux of h7 1e-20 erg/s/cm2/A MaskedColumn 43944
            line_h7_err float64                                                                                                        MaskedColumn 43944
                line_h8 float64                                                                      Line flux of h8 1e-20 erg/s/cm2/A MaskedColumn 44205
            line_h8_err float64                                                                                                        MaskedColumn 44205
                line_h9 float64                                                                      Line flux of h9 1e-20 erg/s/cm2/A MaskedColumn 44333
            line_h9_err float64                                                                                                        MaskedColumn 44333
                line_ha float64                                                                      Line flux of ha 1e-20 erg/s/cm2/A MaskedColumn 39401
            line_ha_err float64                                                                                                        MaskedColumn 39401
          line_hei_6680 float64                                                                Line flux of hei_6680 1e-20 erg/s/cm2/A MaskedColumn 39466
      line_hei_6680_err float64                                                                                                        MaskedColumn 39466
         line_heii_1640 float64                                                               Line flux of heii_1640 1e-20 erg/s/cm2/A MaskedColumn 36364
     line_heii_1640_err float64                                                                                                        MaskedColumn 36364
          line_nii_6549 float64                                                                Line flux of nii_6549 1e-20 erg/s/cm2/A MaskedColumn 39397
      line_nii_6549_err float64                                                                                                        MaskedColumn 39397
          line_nii_6584 float64                                                                Line flux of nii_6584 1e-20 erg/s/cm2/A MaskedColumn 39399
      line_nii_6584_err float64                                                                                                        MaskedColumn 39399
          line_oii_7323 float64                                                                Line flux of oii_7323 1e-20 erg/s/cm2/A MaskedColumn 39822
      line_oii_7323_err float64                                                                                                        MaskedColumn 39822
          line_oii_7332 float64                                                                Line flux of oii_7332 1e-20 erg/s/cm2/A MaskedColumn 39828
      line_oii_7332_err float64                                                                                                        MaskedColumn 39828
          line_sii_6717 float64                                                                Line flux of sii_6717 1e-20 erg/s/cm2/A MaskedColumn 39494
      line_sii_6717_err float64                                                                                                        MaskedColumn 39494
          line_sii_6731 float64                                                                Line flux of sii_6731 1e-20 erg/s/cm2/A MaskedColumn 39479
      line_sii_6731_err float64                                                                                                        MaskedColumn 39479
         line_siii_6314 float64                                                               Line flux of siii_6314 1e-20 erg/s/cm2/A MaskedColumn 39478
     line_siii_6314_err float64                                                                                                        MaskedColumn 39478
                escale0 float64                                                                                                              Column     0
                escale1 float64                                                                                                              Column     0
         line_ciii_1906 float64                                                               Line flux of ciii_1906 1e-20 erg/s/cm2/A MaskedColumn 33196
     line_ciii_1906_err float64                                                                                                        MaskedColumn 33196
          line_niv_1487 float64                                                                Line flux of niv_1487 1e-20 erg/s/cm2/A MaskedColumn 39752
      line_niv_1487_err float64                                                                                                        MaskedColumn 39752
          line_pah_3p29 float64                                                                Line flux of pah_3p29 1e-20 erg/s/cm2/A MaskedColumn 48134
      line_pah_3p29_err float64                                                                                                        MaskedColumn 48134
          line_pah_3p40 float64                                                                Line flux of pah_3p40 1e-20 erg/s/cm2/A MaskedColumn 48134
      line_pah_3p40_err float64                                                                                                        MaskedColumn 48134
         eqw_ariii_7138 float64                                                          Observed-frame equivalent width in ariii_7138 MaskedColumn 15173
         eqw_ariii_7753 float64                                                          Observed-frame equivalent width in ariii_7753 MaskedColumn 16476
                eqw_bra float64                                                                 Observed-frame equivalent width in bra MaskedColumn 50121
                eqw_brb float64                                                                 Observed-frame equivalent width in brb MaskedColumn 45149
                eqw_brd float64                                                                 Observed-frame equivalent width in brd MaskedColumn 39926
                eqw_brg float64                                                                 Observed-frame equivalent width in brg MaskedColumn 42193
          eqw_ciii_1906 float64                                                           Observed-frame equivalent width in ciii_1906 MaskedColumn 33205
           eqw_civ_1549 float64                                                            Observed-frame equivalent width in civ_1549 MaskedColumn 37416
             eqw_ha_nii float64                                                              Observed-frame equivalent width in ha_nii MaskedColumn 26870
                 eqw_hb float64                                                                  Observed-frame equivalent width in hb MaskedColumn 15780
                 eqw_hd float64                                                                  Observed-frame equivalent width in hd MaskedColumn 19054
           eqw_hei_1083 float64                                                            Observed-frame equivalent width in hei_1083 MaskedColumn 23935
           eqw_hei_3889 float64                                                            Observed-frame equivalent width in hei_3889 MaskedColumn 28214
           eqw_hei_5877 float64                                                            Observed-frame equivalent width in hei_5877 MaskedColumn 14154
           eqw_hei_7065 float64                                                            Observed-frame equivalent width in hei_7065 MaskedColumn 14996
           eqw_hei_8446 float64                                                            Observed-frame equivalent width in hei_8446 MaskedColumn 18156
          eqw_heii_1640 float64                                                           Observed-frame equivalent width in heii_1640 MaskedColumn 36368
          eqw_heii_4687 float64                                                           Observed-frame equivalent width in heii_4687 MaskedColumn 34211
                 eqw_hg float64                                                                  Observed-frame equivalent width in hg MaskedColumn 17912
                eqw_lya float64                                                                 Observed-frame equivalent width in lya MaskedColumn 42233
               eqw_mgii float64                                                                Observed-frame equivalent width in mgii MaskedColumn 26165
         eqw_neiii_3867 float64                                                          Observed-frame equivalent width in neiii_3867 MaskedColumn 36508
         eqw_neiii_3968 float64                                                          Observed-frame equivalent width in neiii_3968 MaskedColumn 19812
           eqw_nev_3346 float64                                                            Observed-frame equivalent width in nev_3346 MaskedColumn 23114
          eqw_nevi_3426 float64                                                           Observed-frame equivalent width in nevi_3426 MaskedColumn 22687
          eqw_niii_1750 float64                                                           Observed-frame equivalent width in niii_1750 MaskedColumn 34900
           eqw_niv_1487 float64                                                            Observed-frame equivalent width in niv_1487 MaskedColumn 39754
            eqw_oi_6302 float64                                                             Observed-frame equivalent width in oi_6302 MaskedColumn 13929
                eqw_oii float64                                                                 Observed-frame equivalent width in oii MaskedColumn 21052
           eqw_oii_7325 float64                                                            Observed-frame equivalent width in oii_7325 MaskedColumn 28023
               eqw_oiii float64                                                                Observed-frame equivalent width in oiii MaskedColumn 33982
          eqw_oiii_1663 float64                                                           Observed-frame equivalent width in oiii_1663 MaskedColumn 35847
          eqw_oiii_4363 float64                                                           Observed-frame equivalent width in oiii_4363 MaskedColumn 35027
          eqw_oiii_4959 float64                                                           Observed-frame equivalent width in oiii_4959 MaskedColumn 33706
          eqw_oiii_5007 float64                                                           Observed-frame equivalent width in oiii_5007 MaskedColumn 33587
               eqw_pa10 float64                                                                Observed-frame equivalent width in pa10 MaskedColumn 19660
                eqw_pa8 float64                                                                 Observed-frame equivalent width in pa8 MaskedColumn 20976
                eqw_pa9 float64                                                                 Observed-frame equivalent width in pa9 MaskedColumn 20173
                eqw_paa float64                                                                 Observed-frame equivalent width in paa MaskedColumn 38996
                eqw_pab float64                                                                 Observed-frame equivalent width in pab MaskedColumn 29323
                eqw_pad float64                                                                 Observed-frame equivalent width in pad MaskedColumn 22252
                eqw_pag float64                                                                 Observed-frame equivalent width in pag MaskedColumn 24234
                eqw_pfb float64                                                                 Observed-frame equivalent width in pfb MaskedColumn 51327
                eqw_pfd float64                                                                 Observed-frame equivalent width in pfd MaskedColumn 48117
                eqw_pfe float64                                                                 Observed-frame equivalent width in pfe MaskedColumn 47147
                eqw_pfg float64                                                                 Observed-frame equivalent width in pfg MaskedColumn 49383
                eqw_sii float64                                                                 Observed-frame equivalent width in sii MaskedColumn 27047
          eqw_siii_9068 float64                                                           Observed-frame equivalent width in siii_9068 MaskedColumn 19807
          eqw_siii_9531 float64                                                           Observed-frame equivalent width in siii_9531 MaskedColumn 20940
            line_ha_nii float64                                                            Line flux of combined Ha+NII with 3:1 ratio MaskedColumn 26855
        line_ha_nii_err float64                                                                                                        MaskedColumn 26859
                eqw_h10 float64                                                                 Observed-frame equivalent width in h10 MaskedColumn 44444
                eqw_h11 float64                                                                 Observed-frame equivalent width in h11 MaskedColumn 44547
                eqw_h12 float64                                                                 Observed-frame equivalent width in h12 MaskedColumn 44585
                 eqw_h7 float64                                                                  Observed-frame equivalent width in h7 MaskedColumn 43944
                 eqw_h8 float64                                                                  Observed-frame equivalent width in h8 MaskedColumn 44205
                 eqw_h9 float64                                                                  Observed-frame equivalent width in h9 MaskedColumn 44333
                 eqw_ha float64                                                                  Observed-frame equivalent width in ha MaskedColumn 39403
           eqw_hei_6680 float64                                                            Observed-frame equivalent width in hei_6680 MaskedColumn 39466
           eqw_nii_6549 float64                                                            Observed-frame equivalent width in nii_6549 MaskedColumn 39398
           eqw_nii_6584 float64                                                            Observed-frame equivalent width in nii_6584 MaskedColumn 39400
           eqw_oii_7323 float64                                                            Observed-frame equivalent width in oii_7323 MaskedColumn 39822
           eqw_oii_7332 float64                                                            Observed-frame equivalent width in oii_7332 MaskedColumn 39828
           eqw_sii_6717 float64                                                            Observed-frame equivalent width in sii_6717 MaskedColumn 39494
           eqw_sii_6731 float64                                                            Observed-frame equivalent width in sii_6731 MaskedColumn 39479
          eqw_siii_6314 float64                                                           Observed-frame equivalent width in siii_6314 MaskedColumn 39478
                sn_line float64           .1f                                                                                                Column     0
                  ztime float64                                                                              UNIX time of redshift fit       Column     0
           line_ci_9850 float64                                                                 Line flux of ci_9850 1e-20 erg/s/cm2/A MaskedColumn 21666
       line_ci_9850_err float64                                                                                                        MaskedColumn 21667
        line_feii_11128 float64                                                              Line flux of feii_11128 1e-20 erg/s/cm2/A MaskedColumn 24715
    line_feii_11128_err float64                                                                                                        MaskedColumn 24717
         line_pii_11886 float64                                                               Line flux of pii_11886 1e-20 erg/s/cm2/A MaskedColumn 26724
     line_pii_11886_err float64                                                                                                        MaskedColumn 26724
        line_feii_12570 float64                                                              Line flux of feii_12570 1e-20 erg/s/cm2/A MaskedColumn 28726
    line_feii_12570_err float64                                                                                                        MaskedColumn 28726
            eqw_ci_9850 float64                                                             Observed-frame equivalent width in ci_9850 MaskedColumn 21687
         eqw_feii_11128 float64                                                          Observed-frame equivalent width in feii_11128 MaskedColumn 24742
          eqw_pii_11886 float64                                                           Observed-frame equivalent width in pii_11886 MaskedColumn 26738
         eqw_feii_12570 float64                                                          Observed-frame equivalent width in feii_12570 MaskedColumn 28748
        line_feii_16440 float64                                                              Line flux of feii_16440 1e-20 erg/s/cm2/A MaskedColumn 35778
    line_feii_16440_err float64                                                                                                        MaskedColumn 35778
        line_feii_16877 float64                                                              Line flux of feii_16877 1e-20 erg/s/cm2/A MaskedColumn 36703
    line_feii_16877_err float64                                                                                                        MaskedColumn 36703
               line_brf float64                                                                     Line flux of brf 1e-20 erg/s/cm2/A MaskedColumn 37353
           line_brf_err float64                                                                                                        MaskedColumn 37353
        line_feii_17418 float64                                                              Line flux of feii_17418 1e-20 erg/s/cm2/A MaskedColumn 37428
    line_feii_17418_err float64                                                                                                        MaskedColumn 37428
               line_bre float64                                                                     Line flux of bre 1e-20 erg/s/cm2/A MaskedColumn 38315
           line_bre_err float64                                                                                                        MaskedColumn 38315
        line_feii_18362 float64                                                              Line flux of feii_18362 1e-20 erg/s/cm2/A MaskedColumn 38612
    line_feii_18362_err float64                                                                                                        MaskedColumn 38612
         eqw_feii_16440 float64                                                          Observed-frame equivalent width in feii_16440 MaskedColumn 35789
         eqw_feii_16877 float64                                                          Observed-frame equivalent width in feii_16877 MaskedColumn 36712
                eqw_brf float64                                                                 Observed-frame equivalent width in brf MaskedColumn 37362
         eqw_feii_17418 float64                                                          Observed-frame equivalent width in feii_17418 MaskedColumn 37435
                eqw_bre float64                                                                 Observed-frame equivalent width in bre MaskedColumn 38321
         eqw_feii_18362 float64                                                          Observed-frame equivalent width in feii_18362 MaskedColumn 38621
                  valid    str5                                                         Redshift matches best z from visual inspection       Column     0
                  objid   int64                                                                               Unique source identifier       Column     0
                 z_best float64                                                              Best redshift estimate for unique sources       Column     0
                  ztype    str1                                                                 Source for z_best (G)rating or (P)rism MaskedColumn 16103
                z_prism float64                                                                                                              Column     0
              z_grating float64                                                                                                              Column     0
        phot_correction float64           .2f Scale to photometry -log10(c) = -0.910 log10(flux_radius) + 0.649 log10(profsig) + 0.611 MaskedColumn 15643
       phot_flux_radius float64           .2f                                                      FLUX_RADIUS from photometric source MaskedColumn 15643
                phot_dr float64                                                                                                        MaskedColumn 15643
              file_phot   str44                                                                                                        MaskedColumn 15643
                id_phot   int64                                                                                                        MaskedColumn 15643
          phot_mag_auto float64           .2f                                                                                          MaskedColumn 15643
       phot_f090w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f090w_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f115w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f115w_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f150w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f150w_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f200w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f200w_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f277w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f277w_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f356w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f356w_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f410m_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f410m_etot_1 float64                                                                                                        MaskedColumn 15643
       phot_f444w_tot_1 float64                                                                                                        MaskedColumn 15643
      phot_f444w_etot_1 float64                                                                                                        MaskedColumn 15643
                phot_Av float64                                                                                                        MaskedColumn 15643
              phot_mass float64                                                                                                        MaskedColumn 15643
             phot_restU float64                                                                                                        MaskedColumn 15643
             phot_restV float64                                                                                                        MaskedColumn 15643
             phot_restJ float64                                                                                                        MaskedColumn 15643
                 z_phot float64                                                                                                        MaskedColumn 15643
               phot_LHa float64                                                                                                        MaskedColumn 15643
             phot_LOIII float64                                                                                                        MaskedColumn 15643
              phot_LOII float64                                                                                                        MaskedColumn 15643
                  grade   int64                                                                           Grade from visual inspection MaskedColumn 16373
                 zgrade float64          9.5f                                                          Redshift from visual inspection MaskedColumn 16373
                comment   str74                                                                         Comment from visual inspection MaskedColumn 22904
              mag_f277w float64                                                                                                        MaskedColumn 17905
           obs_239_flux float64                                                                     Spectrum flux in wfc_f814w_t81.dat       Column     0
           obs_205_flux float64                                                                             Spectrum flux in f160w.dat       Column     0
           obs_362_flux float64                                                                     Spectrum flux in jwst_nircam_f070w       Column     0
           obs_363_flux float64                                                                     Spectrum flux in jwst_nircam_f090w       Column     0
           obs_364_flux float64                                                                     Spectrum flux in jwst_nircam_f115w       Column     0
           obs_365_flux float64                                                                     Spectrum flux in jwst_nircam_f150w       Column     0
           obs_366_flux float64                                                                     Spectrum flux in jwst_nircam_f200w       Column     0
           obs_370_flux float64                                                                     Spectrum flux in jwst_nircam_f182m       Column     0
           obs_371_flux float64                                                                     Spectrum flux in jwst_nircam_f210m       Column     0
           obs_375_flux float64                                                                     Spectrum flux in jwst_nircam_f277w       Column     0
           obs_376_flux float64                                                                     Spectrum flux in jwst_nircam_f356w       Column     0
           obs_377_flux float64                                                                     Spectrum flux in jwst_nircam_f444w       Column     0
           obs_379_flux float64                                                                     Spectrum flux in jwst_nircam_f250m       Column     0
           obs_380_flux float64                                                                     Spectrum flux in jwst_nircam_f300m       Column     0
           obs_381_flux float64                                                                     Spectrum flux in jwst_nircam_f335m       Column     0
           obs_382_flux float64                                                                     Spectrum flux in jwst_nircam_f360m       Column     0
           obs_383_flux float64                                                                     Spectrum flux in jwst_nircam_f410m       Column     0
           obs_384_flux float64                                                                     Spectrum flux in jwst_nircam_f430m       Column     0
           obs_385_flux float64                                                                     Spectrum flux in jwst_nircam_f460m       Column     0
           obs_386_flux float64                                                                     Spectrum flux in jwst_nircam_f480m       Column     0
          obs_239_valid   int64                                                                                                              Column     0
           obs_239_frac float64                                                      Fraction of wfc_f814w_t81.dat covered by spectrum       Column     0
            obs_239_err float64                                                                      Spectrum err in wfc_f814w_t81.dat       Column     0
       obs_239_full_err float64                                                                      Spectrum err in wfc_f814w_t81.dat       Column     0
          obs_205_valid   int64                                                                                                              Column     0
           obs_205_frac float64                                                              Fraction of f160w.dat covered by spectrum       Column     0
            obs_205_err float64                                                                              Spectrum err in f160w.dat       Column     0
       obs_205_full_err float64                                                                              Spectrum err in f160w.dat       Column     0
          obs_362_valid   int64                                                                                                              Column     0
           obs_362_frac float64                                                      Fraction of jwst_nircam_f070w covered by spectrum       Column     0
            obs_362_err float64                                                                      Spectrum err in jwst_nircam_f070w       Column     0
       obs_362_full_err float64                                                                      Spectrum err in jwst_nircam_f070w       Column     0
          obs_363_valid   int64                                                                                                              Column     0
           obs_363_frac float64                                                      Fraction of jwst_nircam_f090w covered by spectrum       Column     0
            obs_363_err float64                                                                      Spectrum err in jwst_nircam_f090w       Column     0
       obs_363_full_err float64                                                                      Spectrum err in jwst_nircam_f090w       Column     0
          obs_364_valid   int64                                                                                                              Column     0
           obs_364_frac float64                                                      Fraction of jwst_nircam_f115w covered by spectrum       Column     0
            obs_364_err float64                                                                      Spectrum err in jwst_nircam_f115w       Column     0
       obs_364_full_err float64                                                                      Spectrum err in jwst_nircam_f115w       Column     0
          obs_365_valid   int64                                                                                                              Column     0
           obs_365_frac float64                                                      Fraction of jwst_nircam_f150w covered by spectrum       Column     0
            obs_365_err float64                                                                      Spectrum err in jwst_nircam_f150w       Column     0
       obs_365_full_err float64                                                                      Spectrum err in jwst_nircam_f150w       Column     0
          obs_366_valid   int64                                                                                                              Column     0
           obs_366_frac float64                                                      Fraction of jwst_nircam_f200w covered by spectrum       Column     0
            obs_366_err float64                                                                      Spectrum err in jwst_nircam_f200w       Column     0
       obs_366_full_err float64                                                                      Spectrum err in jwst_nircam_f200w       Column     0
          obs_370_valid   int64                                                                                                              Column     0
           obs_370_frac float64                                                      Fraction of jwst_nircam_f182m covered by spectrum       Column     0
            obs_370_err float64                                                                      Spectrum err in jwst_nircam_f182m       Column     0
       obs_370_full_err float64                                                                      Spectrum err in jwst_nircam_f182m       Column     0
          obs_371_valid   int64                                                                                                              Column     0
           obs_371_frac float64                                                      Fraction of jwst_nircam_f210m covered by spectrum       Column     0
            obs_371_err float64                                                                      Spectrum err in jwst_nircam_f210m       Column     0
       obs_371_full_err float64                                                                      Spectrum err in jwst_nircam_f210m       Column     0
          obs_375_valid   int64                                                                                                              Column     0
           obs_375_frac float64                                                      Fraction of jwst_nircam_f277w covered by spectrum       Column     0
            obs_375_err float64                                                                      Spectrum err in jwst_nircam_f277w       Column     0
       obs_375_full_err float64                                                                      Spectrum err in jwst_nircam_f277w       Column     0
          obs_376_valid   int64                                                                                                              Column     0
           obs_376_frac float64                                                      Fraction of jwst_nircam_f356w covered by spectrum       Column     0
            obs_376_err float64                                                                      Spectrum err in jwst_nircam_f356w       Column     0
       obs_376_full_err float64                                                                      Spectrum err in jwst_nircam_f356w       Column     0
          obs_377_valid   int64                                                                                                              Column     0
           obs_377_frac float64                                                      Fraction of jwst_nircam_f444w covered by spectrum       Column     0
            obs_377_err float64                                                                      Spectrum err in jwst_nircam_f444w       Column     0
       obs_377_full_err float64                                                                      Spectrum err in jwst_nircam_f444w       Column     0
          obs_379_valid   int64                                                                                                              Column     0
           obs_379_frac float64                                                      Fraction of jwst_nircam_f250m covered by spectrum       Column     0
            obs_379_err float64                                                                      Spectrum err in jwst_nircam_f250m       Column     0
       obs_379_full_err float64                                                                      Spectrum err in jwst_nircam_f250m       Column     0
          obs_380_valid   int64                                                                                                              Column     0
           obs_380_frac float64                                                      Fraction of jwst_nircam_f300m covered by spectrum       Column     0
            obs_380_err float64                                                                      Spectrum err in jwst_nircam_f300m       Column     0
       obs_380_full_err float64                                                                      Spectrum err in jwst_nircam_f300m       Column     0
          obs_381_valid   int64                                                                                                              Column     0
           obs_381_frac float64                                                      Fraction of jwst_nircam_f335m covered by spectrum       Column     0
            obs_381_err float64                                                                      Spectrum err in jwst_nircam_f335m       Column     0
       obs_381_full_err float64                                                                      Spectrum err in jwst_nircam_f335m       Column     0
          obs_382_valid   int64                                                                                                              Column     0
           obs_382_frac float64                                                      Fraction of jwst_nircam_f360m covered by spectrum       Column     0
            obs_382_err float64                                                                      Spectrum err in jwst_nircam_f360m       Column     0
       obs_382_full_err float64                                                                      Spectrum err in jwst_nircam_f360m       Column     0
          obs_383_valid   int64                                                                                                              Column     0
           obs_383_frac float64                                                      Fraction of jwst_nircam_f410m covered by spectrum       Column     0
            obs_383_err float64                                                                      Spectrum err in jwst_nircam_f410m       Column     0
       obs_383_full_err float64                                                                      Spectrum err in jwst_nircam_f410m       Column     0
          obs_384_valid   int64                                                                                                              Column     0
           obs_384_frac float64                                                      Fraction of jwst_nircam_f430m covered by spectrum       Column     0
            obs_384_err float64                                                                      Spectrum err in jwst_nircam_f430m       Column     0
       obs_384_full_err float64                                                                      Spectrum err in jwst_nircam_f430m       Column     0
          obs_385_valid   int64                                                                                                              Column     0
           obs_385_frac float64                                                      Fraction of jwst_nircam_f460m covered by spectrum       Column     0
            obs_385_err float64                                                                      Spectrum err in jwst_nircam_f460m       Column     0
       obs_385_full_err float64                                                                      Spectrum err in jwst_nircam_f460m       Column     0
          obs_386_valid   int64                                                                                                              Column     0
           obs_386_frac float64                                                      Fraction of jwst_nircam_f480m covered by spectrum       Column     0
            obs_386_err float64                                                                      Spectrum err in jwst_nircam_f480m       Column     0
       obs_386_full_err float64                                                                      Spectrum err in jwst_nircam_f480m       Column     0
         rest_120_valid   int64                                                                                                              Column     0
          rest_120_frac float64                                                          Fraction of galex1500.res covered by spectrum       Column     0
          rest_120_flux float64                                                                         Spectrum flux in galex1500.res       Column     0
           rest_120_err float64                                                                          Spectrum err in galex1500.res       Column     0
      rest_120_full_err float64                                                                          Spectrum err in galex1500.res       Column     0
         rest_121_valid   int64                                                                                                              Column     0
          rest_121_frac float64                                                          Fraction of galex2500.res covered by spectrum       Column     0
          rest_121_flux float64                                                                         Spectrum flux in galex2500.res       Column     0
           rest_121_err float64                                                                          Spectrum err in galex2500.res       Column     0
      rest_121_full_err float64                                                                          Spectrum err in galex2500.res       Column     0
         rest_218_valid   int64                                                                                                              Column     0
          rest_218_frac float64                                                             Fraction of UV1600.dat covered by spectrum       Column     0
          rest_218_flux float64                                                                            Spectrum flux in UV1600.dat       Column     0
           rest_218_err float64                                                                             Spectrum err in UV1600.dat       Column     0
      rest_218_full_err float64                                                                             Spectrum err in UV1600.dat       Column     0
         rest_219_valid   int64                                                                                                              Column     0
          rest_219_frac float64                                                             Fraction of UV2800.dat covered by spectrum       Column     0
          rest_219_flux float64                                                                            Spectrum flux in UV2800.dat       Column     0
           rest_219_err float64                                                                             Spectrum err in UV2800.dat       Column     0
      rest_219_full_err float64                                                                             Spectrum err in UV2800.dat       Column     0
         rest_270_valid   int64                                                                                                              Column     0
          rest_270_frac float64                                                    Fraction of Tophat_1400_200.dat covered by spectrum       Column     0
          rest_270_flux float64                                                                   Spectrum flux in Tophat_1400_200.dat       Column     0
           rest_270_err float64                                                                    Spectrum err in Tophat_1400_200.dat       Column     0
      rest_270_full_err float64                                                                    Spectrum err in Tophat_1400_200.dat       Column     0
         rest_271_valid   int64                                                                                                              Column     0
          rest_271_frac float64                                                    Fraction of Tophat_1700_200.dat covered by spectrum       Column     0
          rest_271_flux float64                                                                   Spectrum flux in Tophat_1700_200.dat       Column     0
           rest_271_err float64                                                                    Spectrum err in Tophat_1700_200.dat       Column     0
      rest_271_full_err float64                                                                    Spectrum err in Tophat_1700_200.dat       Column     0
         rest_272_valid   int64                                                                                                              Column     0
          rest_272_frac float64                                                    Fraction of Tophat_2200_200.dat covered by spectrum       Column     0
          rest_272_flux float64                                                                   Spectrum flux in Tophat_2200_200.dat       Column     0
           rest_272_err float64                                                                    Spectrum err in Tophat_2200_200.dat       Column     0
      rest_272_full_err float64                                                                    Spectrum err in Tophat_2200_200.dat       Column     0
         rest_274_valid   int64                                                                                                              Column     0
          rest_274_frac float64                                                    Fraction of Tophat_2800_200.dat covered by spectrum       Column     0
          rest_274_flux float64                                                                   Spectrum flux in Tophat_2800_200.dat       Column     0
           rest_274_err float64                                                                    Spectrum err in Tophat_2800_200.dat       Column     0
      rest_274_full_err float64                                                                    Spectrum err in Tophat_2800_200.dat       Column     0
         rest_153_valid   int64                                                                                                              Column     0
          rest_153_frac float64                                           Fraction of maiz-apellaniz_Johnson_U.res covered by spectrum       Column     0
          rest_153_flux float64                                                          Spectrum flux in maiz-apellaniz_Johnson_U.res       Column     0
           rest_153_err float64                                                           Spectrum err in maiz-apellaniz_Johnson_U.res       Column     0
      rest_153_full_err float64                                                           Spectrum err in maiz-apellaniz_Johnson_U.res       Column     0
         rest_154_valid   int64                                                                                                              Column     0
          rest_154_frac float64                                           Fraction of maiz-apellaniz_Johnson_B.res covered by spectrum       Column     0
          rest_154_flux float64                                                          Spectrum flux in maiz-apellaniz_Johnson_B.res       Column     0
           rest_154_err float64                                                           Spectrum err in maiz-apellaniz_Johnson_B.res       Column     0
      rest_154_full_err float64                                                           Spectrum err in maiz-apellaniz_Johnson_B.res       Column     0
         rest_155_valid   int64                                                                                                              Column     0
          rest_155_frac float64                                           Fraction of maiz-apellaniz_Johnson_V.res covered by spectrum       Column     0
          rest_155_flux float64                                                          Spectrum flux in maiz-apellaniz_Johnson_V.res       Column     0
           rest_155_err float64                                                           Spectrum err in maiz-apellaniz_Johnson_V.res       Column     0
      rest_155_full_err float64                                                           Spectrum err in maiz-apellaniz_Johnson_V.res       Column     0
         rest_156_valid   int64                                                                                                              Column     0
          rest_156_frac float64                                                                  Fraction of u.dat covered by spectrum       Column     0
          rest_156_flux float64                                                                                 Spectrum flux in u.dat       Column     0
           rest_156_err float64                                                                                  Spectrum err in u.dat       Column     0
      rest_156_full_err float64                                                                                  Spectrum err in u.dat       Column     0
         rest_157_valid   int64                                                                                                              Column     0
          rest_157_frac float64                                                                  Fraction of g.dat covered by spectrum       Column     0
          rest_157_flux float64                                                                                 Spectrum flux in g.dat       Column     0
           rest_157_err float64                                                                                  Spectrum err in g.dat       Column     0
      rest_157_full_err float64                                                                                  Spectrum err in g.dat       Column     0
         rest_158_valid   int64                                                                                                              Column     0
          rest_158_frac float64                                                                  Fraction of r.dat covered by spectrum       Column     0
          rest_158_flux float64                                                                                 Spectrum flux in r.dat       Column     0
           rest_158_err float64                                                                                  Spectrum err in r.dat       Column     0
      rest_158_full_err float64                                                                                  Spectrum err in r.dat       Column     0
         rest_159_valid   int64                                                                                                              Column     0
          rest_159_frac float64                                                                  Fraction of i.dat covered by spectrum       Column     0
          rest_159_flux float64                                                                                 Spectrum flux in i.dat       Column     0
           rest_159_err float64                                                                                  Spectrum err in i.dat       Column     0
      rest_159_full_err float64                                                                                  Spectrum err in i.dat       Column     0
         rest_160_valid   int64                                                                                                              Column     0
          rest_160_frac float64                                                                  Fraction of z.dat covered by spectrum       Column     0
          rest_160_flux float64                                                                                 Spectrum flux in z.dat       Column     0
           rest_160_err float64                                                                                  Spectrum err in z.dat       Column     0
      rest_160_full_err float64                                                                                  Spectrum err in z.dat       Column     0
         rest_161_valid   int64                                                                                                              Column     0
          rest_161_frac float64                                                                  Fraction of J.res covered by spectrum       Column     0
          rest_161_flux float64                                                                                 Spectrum flux in J.res       Column     0
           rest_161_err float64                                                                                  Spectrum err in J.res       Column     0
      rest_161_full_err float64                                                                                  Spectrum err in J.res       Column     0
         rest_162_valid   int64                                                                                                              Column     0
          rest_162_frac float64                                                                  Fraction of H.res covered by spectrum       Column     0
          rest_162_flux float64                                                                                 Spectrum flux in H.res       Column     0
           rest_162_err float64                                                                                  Spectrum err in H.res       Column     0
      rest_162_full_err float64                                                                                  Spectrum err in H.res       Column     0
         rest_163_valid   int64                                                                                                              Column     0
          rest_163_frac float64                                                                  Fraction of K.res covered by spectrum       Column     0
          rest_163_flux float64                                                                                 Spectrum flux in K.res       Column     0
           rest_163_err float64                                                                                  Spectrum err in K.res       Column     0
      rest_163_full_err float64                                                                                  Spectrum err in K.res       Column     0
         rest_414_valid   int64                                                                                                              Column     0
          rest_414_frac float64                                                            Fraction of synthetic_u covered by spectrum       Column     0
          rest_414_flux float64                                                                           Spectrum flux in synthetic_u       Column     0
           rest_414_err float64                                                                            Spectrum err in synthetic_u       Column     0
      rest_414_full_err float64                                                                            Spectrum err in synthetic_u       Column     0
         rest_415_valid   int64                                                                                                              Column     0
          rest_415_frac float64                                                            Fraction of synthetic_g covered by spectrum       Column     0
          rest_415_flux float64                                                                           Spectrum flux in synthetic_g       Column     0
           rest_415_err float64                                                                            Spectrum err in synthetic_g       Column     0
      rest_415_full_err float64                                                                            Spectrum err in synthetic_g       Column     0
         rest_416_valid   int64                                                                                                              Column     0
          rest_416_frac float64                                                            Fraction of synthetic_i covered by spectrum       Column     0
          rest_416_flux float64                                                                           Spectrum flux in synthetic_i       Column     0
           rest_416_err float64                                                                            Spectrum err in synthetic_i       Column     0
      rest_416_full_err float64                                                                            Spectrum err in synthetic_i       Column     0
                    zrf float64                                                         Redshift used for integrated rest-frame filter       Column     0
                 escale float64                                                                                                              Column     0
                   beta float64                                                                                                        MaskedColumn 27684
          beta_ref_flux float64                                                                                                        MaskedColumn 27683
              beta_npix   int64                                                                                                              Column     0
               beta_wlo float64                                                                                                        MaskedColumn 27683
               beta_whi float64                                                                                                        MaskedColumn 27683
              beta_nmad float64                                                                                                        MaskedColumn 27687
               dla_npix float64                                                                                                        MaskedColumn 27683
              dla_value float64                                                                                                        MaskedColumn 27683
                dla_unc float64                                                                                                        MaskedColumn 27683
            beta_cov_00 float64                                                                                                        MaskedColumn 27683
            beta_cov_01 float64                                                                                                        MaskedColumn 27683
            beta_cov_10 float64                                                                                                        MaskedColumn 27683
            beta_cov_11 float64                                                                                                        MaskedColumn 27683


## Add some preview columns to the table


```python
RGB_URL = "https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord={ra}%2C{dec}"
tab['metafile'] = [m.split('_')[0] for m in tab['msamet']]
SLIT_URL = "https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord={ra}%2C{dec}&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile={metafile}"
FITS_URL = "https://s3.amazonaws.com/msaexp-nirspec/extractions/{root}/{file}"

tab['Thumb'] = [
    "<img src=\"{0}\" height=200px>".format(
        RGB_URL.format(**row['ra','dec'])
    )
    for row in tab
]

tab['Slit_Thumb'] = [
    "<img src=\"{0}\" height=200px>".format(
        SLIT_URL.format(**row['ra','dec','metafile'])
    )
    for row in tab
]

tab['Spectrum_fnu'] = [
    "<img src=\"{0}\" height=200px>".format(
        FITS_URL.format(**row['root','file']).replace('.spec.fits', '.fnu.png')
    )
    for row in tab
]

tab['Spectrum_flam'] = [
    "<img src=\"{0}\" height=200px>".format(
        FITS_URL.format(**row['root','file']).replace('.spec.fits', '.flam.png')
    )
    for row in tab
]

```

# zphot - zspec


```python
import eazy.utils
test = (tab['grade'] == 3) & (tab['z_phot'].filled(-1.) > 0)
test &= (tab['grating'] == 'PRISM')
print(test.sum())
_ = eazy.utils.zphot_zspec(tab['z_phot'][test], tab['z_best'][test], zmax=14)

```

    11200



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_10_1.png)
    



```python
# Counts by mask / program
utils.Unique(tab['root'])
```

       N  value     
    ====  ==========
     309  abell2744-castellano1-v4
     111  abell2744-ddt-v4
     230  abell2744-glass-v4
     137  aurora-gdn01-v4
     147  aurora-gdn02-v4
       9  bd-ic348-gto-v4
      25  bd-orion-gto-v4
     219  bluejay-north-v4
     223  bluejay-south-v4
      50  borg-0037m3337-v4
      38  borg-0314m6712-v4
      37  borg-0409m5317-v4
      36  borg-0440m5244-v4
      37  borg-0859p4114-v4
      45  borg-0955p4528-v4
      38  borg-1033p5051-v4
      43  borg-1437p5044-v4
      30  borg-2203p1851-v4
       5  cantalupo-filament-02-v4
     333  capers-cos01-v4
     416  capers-cos10-v4
     290  capers-cos13-v4
     372  capers-egs44-v4
     395  capers-egs47-v4
     404  capers-egs49-v4
     413  capers-egs53-v4
     324  capers-egs55-v4
     381  capers-egs61-v4
     343  capers-udsp1-v4
     299  capers-udsp2-v4
     278  capers-udsp3-v4
     168  capers-udsp5-v4
     102  cecilia-v4
     151  ceers-ddt-v4
    1720  ceers-v4  
     340  cosmos-curti-v4
       1  cosmos-lae-martin-v4
     301  cosmos-transients-v4
     230  egs-mason-v4
     237  egs-nelsonx-v4
     125  excels-uds01-v4
     125  excels-uds02-v4
     135  excels-uds03-v4
     140  excels-uds04-v4
      26  gdn-chisholm-v4
     187  gdn-pah123-v4
      65  gdn-pah4-v4
      56  gds-barrufet-s156-v4
      82  gds-barrufet-s67-v4
     971  gds-deep-v4
     328  gds-egami-ddt-v4
     236  gds-maseda-v4
     599  gds-rieke-v4
     641  gds-udeep-v4
      96  glazebrook-cos-obs1-v4
     107  glazebrook-cos-obs2-v4
     107  glazebrook-cos-obs3-v4
     119  glazebrook-egs-v4
     236  glazebrook-v4
     190  goodsn-wide-v4
     405  goodsn-wide0-v4
     192  goodsn-wide1-v4
     393  goodsn-wide2-v4
     347  goodsn-wide3-v4
     389  goodsn-wide6-v4
     324  goodsn-wide66-v4
     371  goodsn-wide7-v4
     388  goodsn-wide8-v4
     345  gto-wide-cos01-v4
     380  gto-wide-cos02-v4
     362  gto-wide-cos03-v4
     362  gto-wide-cos04-v4
     378  gto-wide-cos05-v4
    1403  gto-wide-egs1-v4
     344  gto-wide-egs2-v4
     384  gto-wide-uds10-v4
     378  gto-wide-uds11-v4
     330  gto-wide-uds12-v4
     370  gto-wide-uds13-v4
     382  gto-wide-uds14-v4
     507  j0226-wang-v4
     155  j0252m0503-hennawi-02-v4
     158  j0252m0503-hennawi-07-v4
     387  j0910-wang-v4
     232  j1007p2115-hennawi-v4
     548  jades-gdn-v4
     967  jades-gdn09-v4
     961  jades-gdn10-v4
     958  jades-gdn11-v4
    2909  jades-gdn2-v4
     189  jades-gds-w03-v4
     376  jades-gds-w04-v4
     198  jades-gds-w05-v4
     185  jades-gds-w06-v4
     185  jades-gds-w07-v4
     194  jades-gds-w08-v4
     278  jades-gds-w09-v4
    2004  jades-gds-wide-v4
    1305  jades-gds-wide2-v4
     762  jades-gds-wide3-v4
     744  jades-gds02-v4
     681  jades-gds03-v4
     758  jades-gds04-v4
     818  jades-gds05-v4
     739  jades-gds06-v4
     715  jades-gds07-v4
     766  jades-gds08-v4
     649  jades-gds1-v4
     635  jades-gds10-v4
     100  lyc22-schaerer-01-v4
      80  lyc22-schaerer-03-v4
     104  lyc22-schaerer-12-v4
     386  macs1149-stiavelli-v4
      22  macsj0647-hr-v4
      82  macsj0647-single-v4
     133  macsj0647-v4
      27  pearls-transients-v4
     289  rubies-egs51-v4
     386  rubies-egs52-v4
     406  rubies-egs53-v4
     359  rubies-egs61-v4
     445  rubies-egs62-v4
     425  rubies-egs63-v4
     456  rubies-uds1-v4
     415  rubies-uds2-v4
     361  rubies-uds21-v4
     371  rubies-uds22-v4
     347  rubies-uds23-v4
     425  rubies-uds3-v4
     365  rubies-uds31-v4
     432  rubies-uds32-v4
     425  rubies-uds33-v4
     438  rubies-uds41-v4
     408  rubies-uds42-v4
     403  rubies-uds43-v4
     203  rxj2129-ddt-v4
      86  smacs0723-ero-v4
      93  snh0pe-v4 
      92  stark-a1703-v4
     147  stark-rxcj2248-v4
      61  suspense-kriek-v4
     192  ulas-j1120-gto-v4
     152  uncover-61-v4
     180  uncover-62-v4
     557  uncover-v4
     300  whl0137-v4





    <grizli.utils.Unique at 0x148a3c0b0>



## Source counts

Show magnitude, color, redshift distribution as a function of "grade":

- **Grade 3**: Robust redshift from one or more emission absorption features
- **2** Ambiguous continuum features, perhaps only one line or low confidence lines
- **1** No clear features in the spetrum to constrain the redshift
- **0** Spectrum suffers some data quality issue and should


```python
fig, axes = plt.subplots(4,2,figsize=(8,10), sharex=False, sharey=True)

colors = {0: 'magenta', 1: '0.5', 2: 'coral', 3: 'olive'}

# sub = is_rubies
sub = tab['ra'] > 0

sub = sub & True

sub &= tab['z_phot'].filled(-1) > 0
sub &= tab['grating'] == 'PRISM'

un = utils.Unique(tab[sub]['grade'].filled(-1))

blue = -2.5*np.log10(tab['phot_f150w_tot_1'] / tab['phot_f444w_tot_1'])

for i, c in enumerate([3,2,1,0]):

    kws = dict(
        c = np.sqrt(tab[sub][un[c]]['exptime']), vmin=900**0.5, vmax=(5*3600)**0.5, cmap='magma_r',
        # c = 'magenta',
        alpha=0.5, 
        label=f'Grade = {c}',
    )
    
    ax = axes[i][1]
    ax.scatter(blue,
               23.9 - 2.5*np.log10(tab['phot_f444w_tot_1']),
               c='0.8',
               alpha=0.2, 
               label=f'Grade = {c}',
    )

    sc = ax.scatter(blue[sub][un[c]],
               23.9 - 2.5*np.log10(tab[sub]['phot_f444w_tot_1'])[un[c]],
               **kws,
    )
    ax.grid()

    if i < 3:
        ax.set_xticklabels([])

    ax.set_xlim(-2.2, 5.2)
        
    ax = axes[i][0]
    
    ax.scatter(np.log(1+tab['z_phot']),
               23.9 - 2.5*np.log10(tab['phot_f444w_tot_1']),
               c='0.8',
               alpha=0.2, 
               label=f'Grade = {c}' + '\n' + f'N = {un[c].sum()}',
    )

    ax.scatter(np.log(1+tab[sub]['z_phot'][un[c]]),
               23.9 - 2.5*np.log10(tab[sub]['phot_f444w_tot_1'])[un[c]],
               **kws,
    )
    
    ax.grid()
    ax.text(
        0.95, 0.05,
        # f'Grade = {c}',
        f'Grade = {c}' + '\n' + f'N = {un[c].sum()}',
        ha='right', va='bottom', fontsize=9, transform=ax.transAxes)

    if i < 3:
        ax.set_xticklabels([])
    
    xt = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
    ax.set_xlim(0, np.log(1+17))

ax.set_ylabel('mag F444W')

cax = fig.add_axes

cax = fig.add_axes((0.9, 0.1, 0.02, 0.15))
cb = plt.colorbar(sc, cax=cax, orientation='vertical')
ct = [0.5, 1, 2, 4]
cb.set_ticks(np.sqrt(np.array(ct)*3600))
cb.set_ticklabels(ct)
cb.set_label('EXPTIME (h)')

ax.set_ylim(19, 31)

ax.set_xticks(np.log(1+np.array(xt)))
ax.set_xticklabels(xt)
ax.set_xlabel(r'$z_\mathrm{phot}$')

ax = axes[3][1]

ax.set_xlabel('F150W - F444W')

# ax.legend()

fig.tight_layout(pad=1)

```

       N  value     
    ====  ==========
    3713          -1
      93           0
    1283           1
     586           2
    11200           3



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_13_1.png)
    


## PRISM sample for comparision


```python
sample = (tab['grade'] == 3) & (tab['grating'] == 'PRISM')
sample &= tab['z_best'] < 7
sample &= tab['rest_153_frac'] > 0.8
sample &= tab['rest_154_frac'] > 0.8
sample &= tab['rest_155_frac'] > 0.8
sample.sum()
```




    12708



## Interpolate Halpha EQW from nearby filters


```python
import eazy.filters
RES = eazy.filters.FilterFile()

fb, fr = 415, 416
#fb, fr = 155, 416
wb = RES[fb].pivot
wr = RES[fr].pivot

flamb = (1*u.microJansky).to(u.erg/u.second/u.cm**2/u.Angstrom, equivalencies=u.spectral_density(wb*u.Angstrom))
flamr = (1*u.microJansky).to(u.erg/u.second/u.cm**2/u.Angstrom, equivalencies=u.spectral_density(wr*u.Angstrom))

whtb = (1 - np.abs(wb - 6564.)/(wr-wb))# *flamb
whtr = (1 - np.abs(wr - 6564.)/(wr-wb))# *flamr

interp_flux = tab[f'rest_{fb}_flux']*whtb*flamb + tab[f'rest_{fr}_flux']*whtr*flamr

eqw = ((tab['line_ha_nii']*1.e-20*u.erg/u.second/u.cm**2 / (interp_flux / (1+tab['zline'])**1))).value

plt.scatter(
    (np.maximum(tab['eqw_ha_nii'], -100) / (1+tab['zline'])**1)[sample],
    eqw[sample], alpha=0.02
)
plt.plot([0.1, 1e7], [0.1, 1e7], color='r', alpha=0.5)
plt.loglog()
plt.grid()
plt.xlim(0.02, 1.e5); plt.ylim(0.02, 1.e5)
plt.xlabel(r'H$\alpha$ EQW, template fit')
plt.ylabel(r'H$\alpha$ EQW, line flux / estimated continuum')

if 1:
    print('Use interpolated EQW')
    eqw_lim = np.maximum(tab['line_ha_nii'], tab['line_ha_nii_err']*2) * 1.e-20*u.erg/u.second/u.cm**2 / (interp_flux / (1+tab['zline']))
    is_eqw_lim = tab['line_ha_nii_err']*2 > tab['line_ha_nii']
    eqw[is_eqw_lim] = eqw_lim.value[is_eqw_lim]
    tab['ha_eqw_with_limits'] = eqw
    tab['ha_eqw_is_limit'] = is_eqw_lim
    
```

    Use interpolated EQW



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_17_1.png)
    


# Stellar population properties

- Rest-frame colors
- Stellar masses
- ...


```python
UV = -2.5*np.log10(tab['phot_restU'] / tab['phot_restV'])
VJ = -2.5*np.log10(tab['phot_restV'] / tab['phot_restJ'])

UVs = -2.5*np.log10(tab['rest_153_flux'] / tab['rest_155_flux'])
BVs = -2.5*np.log10(tab['rest_154_flux'] / tab['rest_155_flux'])
VJs = -2.5*np.log10(tab['rest_155_flux'] / tab['rest_161_flux'])

eBVs = 2.5/np.log(10) * np.sqrt(
    (tab['rest_154_full_err'] / tab['rest_154_flux'])**2
    + (tab['rest_155_full_err'] / tab['rest_155_flux'])**2
)

ugs = -2.5*np.log10(tab['rest_414_flux'] / tab['rest_415_flux'])
gis = -2.5*np.log10(tab['rest_415_flux'] / tab['rest_416_flux'])

ok_BVs = (tab['rest_154_frac'] > 0.8) & (tab['rest_155_frac'] > 0.8)
ok_gis = (tab['rest_415_frac'] > 0.8) & (tab['rest_416_frac'] > 0.8)

ok_BVs &= eBVs < 0.1

dL = WMAP9.luminosity_distance(tab['zrf']).to('cm')

rest_fV = (tab['rest_155_flux']*u.microJansky).to(
    u.erg/u.second/u.cm**2/u.Angstrom,
    equivalencies=u.spectral_density(5500.*(1+tab['zrf'])*u.Angstrom)
)

rest_fi = (tab['rest_416_flux']*u.microJansky).to(
    u.erg/u.second/u.cm**2/u.Angstrom,
    equivalencies=u.spectral_density(RES[416].pivot * (1+tab['zrf'])*u.Angstrom)
)

LV = (rest_fV * 5500. * u.Angstrom * (1 + tab['zrf']) * 4 * np.pi * dL**2).to(u.Lsun)
Li = (rest_fi * RES[416].pivot * u.Angstrom * (1 + tab['zrf']) * 4 * np.pi * dL**2).to(u.Lsun)

```


```python
# Crude M/Lv ~ B-V from Taylor et al. 2009 for getting a quick stellar mass from the spectrum

log_MLv = -0.734 + 1.404 * (BVs + 0.084)
MassV = log_MLv + np.log10(LV.value)

tab['Mass'] = MassV
tab['Mass'].format = '.2f'
tab['ok_Mass'] = ok_BVs

plt.scatter(
    np.log10(tab['phot_mass'][sample & ok_BVs]),
    MassV[sample & ok_BVs],
    alpha=0.1,
    c=tab['phot_Av'][sample & ok_BVs]
)

plt.plot([5, 12], [5, 12], color='magenta')
plt.grid()
plt.xlim(6, 12)
plt.ylim(6, 12)
plt.xlabel('stellar mass,  eazy photometry')
plt.ylabel(r'$\log M = \log L_V + \log M/L_V$' + '\n' + r'$\log M/L_V \propto (B-V)$')
```




    Text(0, 0.5, '$\\log M = \\log L_V + \\log M/L_V$\n$\\log M/L_V \\propto (B-V)$')




    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_20_1.png)
    


## Compare rest-frame colors

The table includes rest-frame bandpass flux densities 1) estimated from the broad-band photometry (at the photo-z) and 2) integrated directly through the spectra at the measured redshift.  

The colors derived from the  grizli/DJA *photometry* are those of the best-fit photo-z template combination, not a noisy interpolation, so they can show banding effects resulting from the discrete combination of templates.


```python
fig, axes = plt.subplots(1,2,figsize=(8,5), sharex=True, sharey=True)

axes[0].scatter(
    VJ[sample], UV[sample], alpha=0.1,
    c=tab['ha_eqw_with_limits'][sample], vmin=0, vmax=200, cmap='RdYlBu'
)
axes[0].set_xlabel(r'$(V-J)$' + ', eazy template')
axes[0].set_ylabel(r'$(U-V)$')

axes[1].scatter(
    VJs[sample], UVs[sample], alpha=0.1,
    c=tab['ha_eqw_with_limits'][sample], vmin=0, vmax=200, cmap='RdYlBu'
)

sc = axes[1].scatter(
    VJs[sample][:1], UVs[sample][:1], alpha=0.5,
    c=tab['ha_eqw_with_limits'][sample][:1], vmin=0, vmax=200, cmap='RdYlBu'
)

axes[1].set_xlabel(r'$(V-J)$' + ', spectrum')

for ax in axes:
    ax.set_xlim(-1.2, 4.2)
    ax.set_ylim(-0.8, 4.2)
    ax.grid()

cax = fig.add_axes((0.85, 0.2, 0.02, 0.25))
cb = plt.colorbar(sc, cax=cax, orientation='vertical')
cb.set_label(r'EQW H$\alpha$')

fig.tight_layout(pad=1)
```


    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_22_0.png)
    



```python
plt.scatter(
    tab['z_best'][sample],
    # np.log10(tab['phot_mass'])[sample],
    tab['Mass'][sample],
    alpha=0.1,
    c=tab['ha_eqw_with_limits'][sample], vmin=0, vmax=200, cmap='RdYlBu'
)
plt.ylim(7, 12)
plt.grid()
plt.xlabel('redshift')
plt.ylabel('rough stellar mass')
```




    Text(0, 0.5, 'rough stellar mass')




    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_23_1.png)
    



```python
# Make a preview table
massive = sample & (tab['z_best'] > 4.) & (MassV > 10.5) & (tab['grating'] == 'PRISM') & ok_BVs

if 0:
    tab['root','file','z_best','Mass','ha_eqw_with_limits','Thumb','Slit_Thumb','Spectrum_fnu', 'Spectrum_flam'][massive].write_sortable_html(
        '/tmp/massive.html',
        max_lines=1000,
        localhost=False,
    )
    
print(f"massive test sample: {massive.sum()}")
```

    massive test sample: 69



```python
from IPython.display import display, Markdown, Latex

so = np.argsort(tab['Mass'][massive])[::-1]
so = so[:32]

df = tab['root','file','z_best','Mass','ha_eqw_with_limits','Thumb','Slit_Thumb','Spectrum_fnu', 'Spectrum_flam'][massive][so].to_pandas()

display(Markdown(df.to_markdown()))
```


|    | root                | file                                                |   z_best |    Mass |   ha_eqw_with_limits | Thumb                                                                                                                                                                                                         | Slit_Thumb                                                                                                                                                                                                                                                  | Spectrum_fnu                                                                                                                                       | Spectrum_flam                                                                                                                                       |
|---:|:--------------------|:----------------------------------------------------|---------:|--------:|---------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | j0910-wang-v4       | j0910-wang-v4_prism-clear_2028_12910.spec.fits      |  6.62142 | 12.0515 |             54.4902  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=137.72721162%2C-4.23520691" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=137.72721162%2C-4.23520691&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02028001001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/j0910-wang-v4/j0910-wang-v4_prism-clear_2028_12910.fnu.png" height=200px>            | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/j0910-wang-v4/j0910-wang-v4_prism-clear_2028_12910.flam.png" height=200px>            |
|  1 | rubies-uds23-v4     | rubies-uds23-v4_prism-clear_4233_166691.spec.fits   |  4.06673 | 11.9254 |             11.4969  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.36378034%2C-5.11191402" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.36378034%2C-5.11191402&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233002003" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_166691.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_166691.flam.png" height=200px>       |
|  2 | uncover-61-v4       | uncover-61-v4_prism-clear_2561_13416.spec.fits      |  4.02262 | 11.7896 |            114.235   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.57556471%2C-30.42438021" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.57556471%2C-30.42438021&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02561006001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-61-v4/uncover-61-v4_prism-clear_2561_13416.fnu.png" height=200px>            | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-61-v4/uncover-61-v4_prism-clear_2561_13416.flam.png" height=200px>            |
|  3 | rubies-egs52-v4     | rubies-egs52-v4_prism-clear_4233_9809.spec.fits     |  5.68123 | 11.6563 |            197.61    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=215.01729764%2C52.88015836" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=215.01729764%2C52.88015836&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233005002" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs52-v4/rubies-egs52-v4_prism-clear_4233_9809.fnu.png" height=200px>         | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs52-v4/rubies-egs52-v4_prism-clear_4233_9809.flam.png" height=200px>         |
|  4 | jades-gdn-v4        | jades-gdn-v4_prism-clear_1181_68797.spec.fits       |  5.03971 | 11.6303 |           1054.65    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2291371%2C62.1461898" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2291371%2C62.1461898&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01181098001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn-v4/jades-gdn-v4_prism-clear_1181_68797.fnu.png" height=200px>              | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn-v4/jades-gdn-v4_prism-clear_1181_68797.flam.png" height=200px>              |
|  5 | rubies-uds22-v4     | rubies-uds22-v4_prism-clear_4233_114988.spec.fits   |  4.36474 | 11.5051 |             94.5801  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.29794136%2C-5.18436854" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.29794136%2C-5.18436854&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233002002" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds22-v4/rubies-uds22-v4_prism-clear_4233_114988.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds22-v4/rubies-uds22-v4_prism-clear_4233_114988.flam.png" height=200px>       |
|  6 | gto-wide-uds13-v4   | gto-wide-uds13-v4_prism-clear_1215_1472.spec.fits   |  4.55596 | 11.4348 |             14.736   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.33731548%2C-5.1436736" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.33731548%2C-5.1436736&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01215013001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_prism-clear_1215_1472.fnu.png" height=200px>     | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_prism-clear_1215_1472.flam.png" height=200px>     |
|  7 | uncover-v4          | uncover-v4_prism-clear_2561_45924.spec.fits         |  4.4673  | 11.3522 |            104.309   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.58476007%2C-30.34362753" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.58476007%2C-30.34362753&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02561002004" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-v4/uncover-v4_prism-clear_2561_45924.fnu.png" height=200px>                  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-v4/uncover-v4_prism-clear_2561_45924.flam.png" height=200px>                  |
|  8 | uncover-62-v4       | uncover-62-v4_prism-clear_2561_58453.spec.fits      |  4.4673  | 11.2252 |            969.994   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.58475839%2C-30.34362894" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.58475839%2C-30.34362894&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02561006002" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-62-v4/uncover-62-v4_prism-clear_2561_58453.fnu.png" height=200px>            | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-62-v4/uncover-62-v4_prism-clear_2561_58453.flam.png" height=200px>            |
|  9 | gds-barrufet-s67-v4 | gds-barrufet-s67-v4_prism-clear_2198_1260.spec.fits |  4.4319  | 11.2251 |             72.7017  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.07485578%2C-27.87589702" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.07485578%2C-27.87589702&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02198003001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gds-barrufet-s67-v4/gds-barrufet-s67-v4_prism-clear_2198_1260.fnu.png" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gds-barrufet-s67-v4/gds-barrufet-s67-v4_prism-clear_2198_1260.flam.png" height=200px> |
| 10 | rubies-egs63-v4     | rubies-egs63-v4_prism-clear_4233_49140.spec.fits    |  6.68959 | 11.1816 |            657.49    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.89224786%2C52.87740968" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.89224786%2C52.87740968&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233006003" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs63-v4/rubies-egs63-v4_prism-clear_4233_49140.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs63-v4/rubies-egs63-v4_prism-clear_4233_49140.flam.png" height=200px>        |
| 11 | rubies-uds42-v4     | rubies-uds42-v4_prism-clear_4233_807469.spec.fits   |  6.77538 | 11.1462 |           4951.05    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.3761391%2C-5.3103658" height=200px>    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.3761391%2C-5.3103658&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233004002" height=200px>    | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds42-v4/rubies-uds42-v4_prism-clear_4233_807469.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds42-v4/rubies-uds42-v4_prism-clear_4233_807469.flam.png" height=200px>       |
| 12 | rubies-egs61-v4     | rubies-egs61-v4_prism-clear_4233_55604.spec.fits    |  6.98435 | 11.1174 |           2762.98    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.98302557%2C52.9560013" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.98302557%2C52.9560013&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233006001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_55604.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_55604.flam.png" height=200px>        |
| 13 | uncover-62-v4       | uncover-62-v4_prism-clear_2561_59554.spec.fits      |  4.47252 | 11.0693 |            155.997   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.57201994%2C-30.34249594" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.57201994%2C-30.34249594&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02561006002" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-62-v4/uncover-62-v4_prism-clear_2561_59554.fnu.png" height=200px>            | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-62-v4/uncover-62-v4_prism-clear_2561_59554.flam.png" height=200px>            |
| 14 | rubies-uds31-v4     | rubies-uds31-v4_prism-clear_4233_149494.spec.fits   |  4.62235 | 11.0691 |              5.34271 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.39967589%2C-5.13634805" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.39967589%2C-5.13634805&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233003001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds31-v4/rubies-uds31-v4_prism-clear_4233_149494.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds31-v4/rubies-uds31-v4_prism-clear_4233_149494.flam.png" height=200px>       |
| 15 | capers-egs49-v4     | capers-egs49-v4_prism-clear_6368_11585.spec.fits    |  6.68959 | 10.9733 |            480.117   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.8922488%2C52.8774032" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.8922488%2C52.8774032&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw06368049001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/capers-egs49-v4/capers-egs49-v4_prism-clear_6368_11585.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/capers-egs49-v4/capers-egs49-v4_prism-clear_6368_11585.flam.png" height=200px>        |
| 16 | rubies-uds23-v4     | rubies-uds23-v4_prism-clear_4233_140707.spec.fits   |  4.62    | 10.908  |             10.0372  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.36508449%2C-5.14884841" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.36508449%2C-5.14884841&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233002003" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_140707.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_140707.flam.png" height=200px>       |
| 17 | rubies-uds23-v4     | rubies-uds23-v4_prism-clear_4233_148866.spec.fits   |  5.22256 | 10.9076 |            262.927   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.32643349%2C-5.13738186" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.32643349%2C-5.13738186&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233002003" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_148866.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_148866.flam.png" height=200px>       |
| 18 | egs-nelsonx-v4      | egs-nelsonx-v4_prism-clear_4106_57146.spec.fits     |  6.68959 | 10.8953 |            471.6     | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.89224643%2C52.87740951" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.89224643%2C52.87740951&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04106006001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/egs-nelsonx-v4/egs-nelsonx-v4_prism-clear_4106_57146.fnu.png" height=200px>          | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/egs-nelsonx-v4/egs-nelsonx-v4_prism-clear_4106_57146.flam.png" height=200px>          |
| 19 | gto-wide-uds13-v4   | gto-wide-uds13-v4_prism-clear_1215_6001.spec.fits   |  4.58301 | 10.8825 |            716.686   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.36424834%2C-5.1977302" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.36424834%2C-5.1977302&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01215013001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_prism-clear_1215_6001.fnu.png" height=200px>     | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-uds13-v4/gto-wide-uds13-v4_prism-clear_1215_6001.flam.png" height=200px>     |
| 20 | rubies-uds2-v4      | rubies-uds2-v4_prism-clear_b28.spec.fits            |  4.36275 | 10.8802 |              5.61715 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233001002" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_b28.fnu.png" height=200px>                 | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_b28.flam.png" height=200px>                 |
| 21 | rubies-uds2-v4      | rubies-uds2-v4_prism-clear_4233_b28.spec.fits       |  4.36275 | 10.8801 |              5.59212 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233001002" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_4233_b28.fnu.png" height=200px>            | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_4233_b28.flam.png" height=200px>            |
| 22 | rubies-egs61-v4     | rubies-egs61-v4_prism-clear_4233_75646.spec.fits    |  4.90002 | 10.874  |             24.3336  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233006001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_75646.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_75646.flam.png" height=200px>        |
| 23 | goodsn-wide2-v4     | goodsn-wide2-v4_prism-clear_1211_10.spec.fits       |  4.14019 | 10.8389 |            236.904   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.14356704%2C62.16166621" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.14356704%2C62.16166621&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01211014001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/goodsn-wide2-v4/goodsn-wide2-v4_prism-clear_1211_10.fnu.png" height=200px>           | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/goodsn-wide2-v4/goodsn-wide2-v4_prism-clear_1211_10.flam.png" height=200px>           |
| 24 | uncover-61-v4       | uncover-61-v4_prism-clear_2561_21547.spec.fits      |  5.05789 | 10.8387 |            553.345   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.55083778%2C-30.40659783" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.55083778%2C-30.40659783&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02561006001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-61-v4/uncover-61-v4_prism-clear_2561_21547.fnu.png" height=200px>            | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-61-v4/uncover-61-v4_prism-clear_2561_21547.flam.png" height=200px>            |
| 25 | jades-gdn2-v4       | jades-gdn2-v4_prism-clear_1181_954.spec.fits        |  6.76117 | 10.8335 |           1997.48    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.1519657%2C62.2596352" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.1519657%2C62.2596352&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01181007001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn2-v4/jades-gdn2-v4_prism-clear_1181_954.fnu.png" height=200px>              | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn2-v4/jades-gdn2-v4_prism-clear_1181_954.flam.png" height=200px>              |
| 26 | rubies-egs53-v4     | rubies-egs53-v4_prism-clear_4233_42046.spec.fits    |  5.27719 | 10.8159 |           1213.54    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.79536781%2C52.78884663" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.79536781%2C52.78884663&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233005003" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs53-v4/rubies-egs53-v4_prism-clear_4233_42046.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs53-v4/rubies-egs53-v4_prism-clear_4233_42046.flam.png" height=200px>        |
| 27 | snh0pe-v4           | snh0pe-v4_prism-clear_4446_274.spec.fits            |  4.10583 | 10.8132 |              4.80224 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=171.82361288%2C42.46963868" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=171.82361288%2C42.46963868&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04446001001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/snh0pe-v4/snh0pe-v4_prism-clear_4446_274.fnu.png" height=200px>                      | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/snh0pe-v4/snh0pe-v4_prism-clear_4446_274.flam.png" height=200px>                      |
| 28 | rubies-uds23-v4     | rubies-uds23-v4_prism-clear_4233_155916.spec.fits   |  4.09409 | 10.7958 |             47.1011  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.3170308%2C-5.12761145" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.3170308%2C-5.12761145&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233002003" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_155916.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds23-v4/rubies-uds23-v4_prism-clear_4233_155916.flam.png" height=200px>       |
| 29 | uncover-v4          | uncover-v4_prism-clear_2561_4286.spec.fits          |  5.83522 | 10.7673 |            730.932   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.61920101%2C-30.42327034" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=3.61920101%2C-30.42327034&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02561002002" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-v4/uncover-v4_prism-clear_2561_4286.fnu.png" height=200px>                   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/uncover-v4/uncover-v4_prism-clear_2561_4286.flam.png" height=200px>                   |
| 30 | jades-gds-w07-v4    | jades-gds-w07-v4_prism-clear_1212_6071.spec.fits    |  5.55195 | 10.7579 |           1022.83    | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.16270355%2C-27.8731285" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.16270355%2C-27.8731285&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01212007001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gds-w07-v4/jades-gds-w07-v4_prism-clear_1212_6071.fnu.png" height=200px>       | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gds-w07-v4/jades-gds-w07-v4_prism-clear_1212_6071.flam.png" height=200px>       |
| 31 | rubies-uds43-v4     | rubies-uds43-v4_prism-clear_4233_19735.spec.fits    |  4.8047  | 10.7567 |            241.777   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.30109423%2C-5.28798532" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.30109423%2C-5.28798532&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233004003" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds43-v4/rubies-uds43-v4_prism-clear_4233_19735.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds43-v4/rubies-uds43-v4_prism-clear_4233_19735.flam.png" height=200px>        |


## Read a spectrum

![ruby](https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_75646.fnu.png)


```python
import msaexp.spectrum
spec_file = 'rubies-egs61-v4_prism-clear_4233_75646.spec.fits'
row = tab[tab['file'] == spec_file][0]
spec = msaexp.spectrum.SpectrumSampler(FITS_URL.format(**row))
```


```python
row['Mass']
```




    10.873998434439217




```python
spec.spec.info
```




    <GTable length=473>
        name     dtype  unit                description                   class     n_bad
    ----------- ------- ---- ----------------------------------------- ------------ -----
           wave float64                                                      Column     0
           flux float64                                                      Column     0
            err float64                                                      Column     0
            sky float64  uJy                                           MaskedColumn     5
      path_corr float64                                                MaskedColumn     5
           npix float64                                                      Column     0
       flux_sum float64                                                      Column     0
    profile_sum float64                                                      Column     0
        var_sum float64                                                      Column     0
           corr float64                                                      Column     0
         escale float64                                                      Column     0
       full_err float64  uJy                                                 Column     0
          valid    bool                                                      Column     0
              R float64      Spectral resolution from tabulated curves       Column     0
        to_flam float64                                                      Column     0




```python
plt.plot(spec['wave'], spec['flux'],
         label="{file}\nz={z_best:.3f}".format(**row))
plt.legend()
```




    <matplotlib.legend.Legend at 0x37e969970>




    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_30_1.png)
    


# All `msaexp` PRISM spectra in a single table


```python
combined_spectra_file = "dja_msaexp_emission_lines_v4.0.prism_spectra.fits"

if os.path.exists(combined_spectra_file):
    prism_spectra = utils.read_catalog(combined_spectra_file)
else:
    # Combined prism spectra in a single big table (595 Mb)
    prism_spectra = utils.read_catalog(
        download_file(
            f"https://s3.amazonaws.com/msaexp-nirspec/extractions/{combined_spectra_file}",
            cache=True
        ),
        format='fits',
    )
```


```python
is_prism = tab['grating'] == 'PRISM'
tab['prism_idx'] = 0
tab['prism_idx'][is_prism] = np.arange(is_prism.sum())

print(f"""
PRISM spectra in the merged catalog: {is_prism.sum()}
PRISM spectra in the combined table: {prism_spectra['flux'].shape[1]}
""")
```

    
    PRISM spectra in the merged catalog: 26913
    PRISM spectra in the combined table: 26913
    



```python
valid_count = prism_spectra['valid'].sum(axis=0)
valid_spec = valid_count > (valid_count.max() - 8)
```


```python
row = tab[tab['file'] == spec_file][0]

plt.plot(
    spec['wave'], spec['flux'],
    lw=2, label='Single spectrum'
)

plt.plot(
    prism_spectra['wave'], prism_spectra['flux'][:, row['prism_idx']],
    alpha=0.5, label='From combined table'
)

plt.legend()
```




    <matplotlib.legend.Legend at 0x37fa98bf0>




    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_35_1.png)
    


## "Stacked" spectrum

Stacking prism spectra isn't trivial due to the variable dispersion and wavelength sampling.  Here just plot a subset on top of eachother.


```python
norm_column = 'rest_416_flux'
print(f"Normalization column: '{norm_column}' = {tab[norm_column].description}")

flux_norm = prism_spectra['flux'] / tab[norm_column][is_prism]

# Subset
zi = row['z_best']
dz = 0.05

sample = (tab['z_best'] > zi - dz) & (tab['z_best'] < zi + dz)

sub_sample = sample[is_prism] & valid_spec
sub_idx = np.where(sub_sample)[0]

z_sample = tab['z_best'][is_prism][sample[is_prism] & valid_spec]

fig, axes = plt.subplots(2,1,figsize=(10,7), sharex=False, sharey=True)

for j, z in enumerate(z_sample):
    axes[0].plot(
        prism_spectra['wave'],
        flux_norm[:, sub_idx[j]],
        alpha=0.1
    )
    
    axes[1].plot(
        prism_spectra['wave'] / (1 + z),
        flux_norm[:, sub_idx[j]],
        alpha=0.1
    )


axes[0].set_ylim(-1, 10)
```

    Normalization column: 'rest_416_flux' = Spectrum flux in synthetic_i





    (-1.0, 10.0)




    
![png]({{ site.baseurl }}/assets/post_files/2025-05-01-nirspec-merged-table-v4_files/nirspec-merged-table-v4_37_2.png)
    


# "Nearest neighbor" spectra

Simple "nearest neighbors" of the normalized spectra.


```python
fix_flux_norm = flux_norm*1.
fix_flux_norm[~np.isfinite(flux_norm)] = 0

tr = cKDTree(fix_flux_norm[:, valid_spec].T)
tr_ds, tr_idx = tr.query(fix_flux_norm[:, row['prism_idx']], k=16)

df = tab['root','file','z_best','Mass','ha_eqw_with_limits','Thumb','Slit_Thumb','Spectrum_fnu', 'Spectrum_flam'][is_prism][valid_spec][tr_idx].to_pandas()

display(Markdown(df.to_markdown()))

```


|    | root                   | file                                                    |   z_best |    Mass |   ha_eqw_with_limits | Thumb                                                                                                                                                                                                         | Slit_Thumb                                                                                                                                                                                                                                                  | Spectrum_fnu                                                                                                                                              | Spectrum_flam                                                                                                                                              |
|---:|:-----------------------|:--------------------------------------------------------|---------:|--------:|---------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | rubies-egs61-v4        | rubies-egs61-v4_prism-clear_4233_75646.spec.fits        |  4.90002 | 10.874  |             24.3336  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233006001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_75646.fnu.png" height=200px>               | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-egs61-v4/rubies-egs61-v4_prism-clear_4233_75646.flam.png" height=200px>               |
|  1 | gds-barrufet-s67-v4    | gds-barrufet-s67-v4_prism-clear_2198_8777.spec.fits     |  4.65301 | 10.6769 |              8.26113 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.10820397%2C-27.82518775" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.10820397%2C-27.82518775&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02198003001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gds-barrufet-s67-v4/gds-barrufet-s67-v4_prism-clear_2198_8777.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gds-barrufet-s67-v4/gds-barrufet-s67-v4_prism-clear_2198_8777.flam.png" height=200px>        |
|  2 | gds-barrufet-s67-v4    | gds-barrufet-s67-v4_prism-clear_2198_8290.spec.fits     |  4.34386 | 10.5556 |              4.0581  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.08187859%2C-27.82879899" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.08187859%2C-27.82879899&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02198003001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gds-barrufet-s67-v4/gds-barrufet-s67-v4_prism-clear_2198_8290.fnu.png" height=200px>        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gds-barrufet-s67-v4/gds-barrufet-s67-v4_prism-clear_2198_8290.flam.png" height=200px>        |
|  3 | jades-gdn09-v4         | jades-gdn09-v4_prism-clear_1181_72127.spec.fits         |  4.13368 | 10.5771 |             75.7974  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2657184%2C62.1683933" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2657184%2C62.1683933&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01181009001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn09-v4/jades-gdn09-v4_prism-clear_1181_72127.fnu.png" height=200px>                 | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn09-v4/jades-gdn09-v4_prism-clear_1181_72127.flam.png" height=200px>                 |
|  4 | glazebrook-cos-obs1-v4 | glazebrook-cos-obs1-v4_prism-clear_2565_10559.spec.fits |  4.28971 | 10.5518 |              3.80496 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=150.07143593%2C2.29117893" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=150.07143593%2C2.29117893&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02565301001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-cos-obs1-v4/glazebrook-cos-obs1-v4_prism-clear_2565_10559.fnu.png" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-cos-obs1-v4/glazebrook-cos-obs1-v4_prism-clear_2565_10559.flam.png" height=200px> |
|  5 | jades-gds-wide-v4      | jades-gds-wide-v4_prism-clear_1180_12619.spec.fits      |  3.60805 | 10.6324 |             27.8163  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.1969096%2C-27.7605277" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.1969096%2C-27.7605277&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01180029001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gds-wide-v4/jades-gds-wide-v4_prism-clear_1180_12619.fnu.png" height=200px>           | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gds-wide-v4/jades-gds-wide-v4_prism-clear_1180_12619.flam.png" height=200px>           |
|  6 | rubies-uds2-v4         | rubies-uds2-v4_prism-clear_b28.spec.fits                |  4.36275 | 10.8802 |              5.61715 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233001002" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_b28.fnu.png" height=200px>                        | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_b28.flam.png" height=200px>                        |
|  7 | rubies-uds2-v4         | rubies-uds2-v4_prism-clear_4233_b28.spec.fits           |  4.36275 | 10.8801 |              5.59212 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.2805153%2C-5.21721404&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233001002" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_4233_b28.fnu.png" height=200px>                   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds2-v4/rubies-uds2-v4_prism-clear_4233_b28.flam.png" height=200px>                   |
|  8 | glazebrook-cos-obs3-v4 | glazebrook-cos-obs3-v4_prism-clear_2565_20115.spec.fits |  3.71293 | 11.2231 |              2.61723 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=150.06146711%2C2.37868632" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=150.06146711%2C2.37868632&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02565007001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-cos-obs3-v4/glazebrook-cos-obs3-v4_prism-clear_2565_20115.fnu.png" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-cos-obs3-v4/glazebrook-cos-obs3-v4_prism-clear_2565_20115.flam.png" height=200px> |
|  9 | gto-wide-egs1-v4       | gto-wide-egs1-v4_prism-clear_1213_4358.spec.fits        |  4.28982 | 10.6918 |             21.9825  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=215.03907944%2C53.0027735" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=215.03907944%2C53.0027735&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01213002001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-egs1-v4/gto-wide-egs1-v4_prism-clear_1213_4358.fnu.png" height=200px>              | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/gto-wide-egs1-v4/gto-wide-egs1-v4_prism-clear_1213_4358.flam.png" height=200px>              |
| 10 | jades-gdn09-v4         | jades-gdn09-v4_prism-clear_1181_80660.spec.fits         |  4.39946 | 10.2177 |             25.751   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2754487%2C62.2141353" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2754487%2C62.2141353&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01181009001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn09-v4/jades-gdn09-v4_prism-clear_1181_80660.fnu.png" height=200px>                 | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn09-v4/jades-gdn09-v4_prism-clear_1181_80660.flam.png" height=200px>                 |
| 11 | glazebrook-v4          | glazebrook-v4_prism-clear_2565_10459.spec.fits          |  3.98685 | 10.6829 |              4.65304 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.34034528%2C-5.24130895" height=200px>  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.34034528%2C-5.24130895&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02565100001" height=200px>  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-v4/glazebrook-v4_prism-clear_2565_10459.fnu.png" height=200px>                   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-v4/glazebrook-v4_prism-clear_2565_10459.flam.png" height=200px>                   |
| 12 | jades-gdn-v4           | jades-gdn-v4_prism-clear_1181_76320.spec.fits           |  3.23859 | 10.3316 |              4.69578 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2214567%2C62.1924022" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=189.2214567%2C62.1924022&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01181098001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn-v4/jades-gdn-v4_prism-clear_1181_76320.fnu.png" height=200px>                     | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gdn-v4/jades-gdn-v4_prism-clear_1181_76320.flam.png" height=200px>                     |
| 13 | capers-egs49-v4        | capers-egs49-v4_prism-clear_6368_7806.spec.fits         |  3.44385 | 10.285  |             33.2528  | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.8790898%2C52.8880604" height=200px>   | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.8790898%2C52.8880604&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw06368049001" height=200px>   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/capers-egs49-v4/capers-egs49-v4_prism-clear_6368_7806.fnu.png" height=200px>                | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/capers-egs49-v4/capers-egs49-v4_prism-clear_6368_7806.flam.png" height=200px>                |
| 14 | glazebrook-v4          | glazebrook-v4_prism-clear_2565_35168.spec.fits          |  3.71777 | 10.2866 |              7.84772 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.48515%2C-5.1578067" height=200px>      | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=34.48515%2C-5.1578067&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw02565300001" height=200px>      | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-v4/glazebrook-v4_prism-clear_2565_35168.fnu.png" height=200px>                   | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/glazebrook-v4/glazebrook-v4_prism-clear_2565_35168.flam.png" height=200px>                   |
| 15 | jades-gds-w03-v4       | jades-gds-w03-v4_prism-clear_1212_1231.spec.fits        |  4.34386 | 10.4459 |              3.51736 | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.08191171%2C-27.82880802" height=200px> | <img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=53.08191171%2C-27.82880802&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw01212003001" height=200px> | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gds-w03-v4/jades-gds-w03-v4_prism-clear_1212_1231.fnu.png" height=200px>              | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/jades-gds-w03-v4/jades-gds-w03-v4_prism-clear_1212_1231.flam.png" height=200px>              |


## Thumbnail API

The DJA thumbnail API can create thumbnail figures and FITS cutouts of a requested set of filters at a particular coordinate.M


```python
from IPython.display import Image
print(RGB_URL.format(**row))
Image(url=RGB_URL.format(**row), height=300, width=300)

```

    https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831





<img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=2.0&asinh=True&filters=f115w-clear%2Cf277w-clear%2Cf444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831" width="300" height="300"/>




```python
print(SLIT_URL.format(**row))
Image(url=SLIT_URL.format(**row), height=300, width=300)
```

    https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233006001





<img src="https://grizli-cutout.herokuapp.com/thumb?size=1.5&scl=4.0&invert=True&filters=f444w-clear&rgb_scl=1.5%2C0.74%2C1.3&pl=2&coord=214.91554591%2C52.94901831&nirspec=True&dpi_scale=6&nrs_lw=0.5&nrs_alpha=0.8&metafile=jw04233006001" width="300" height="300"/>


