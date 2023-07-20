---
layout: page
title: NIRSpec Wavecal Spectra
showSpecDataset: true
navigation_weight: 11
---

Here we provide [msaexp](https://github.com/gbrammer/msaexp) reductions of the longslit spectra from [CAL-1125](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1125&observatory=JWST) of the wavelength calibration source [IRAS 05248 7007 (SMP LMC 58)](http://simbad.u-strasbg.fr/simbad/sim-id?Ident=LHA+120-N+133), a compact planetary nebula in the LMC.  Note that the source has a radial velocity of [294.9 ± 22.7 km/s](http://simbad.u-strasbg.fr/simbad/sim-id?mescat.velocities=on&mescat.pm=on&mescat.mk=on&Ident=%403117300&Name=LHA+120-N+133&submit=display+selected+measurements#lab_meas) [(Reid & Parker 2006)](https://ui.adsabs.harvard.edu/abs/2006MNRAS.373..521R/abstract).

### Extracted spectra
File listing: [files.csv]({{ site.baseurl }}/data/nirspec-wavecal/files.csv)

| File | Filter | Grating |
|------|:------:|:-------:|
| [calib_g140h-f070lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g140h-f070lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F070LP | G140H | 
| [calib_g140h-f100lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g140h-f100lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F100LP | G140H | 
| [calib_g140m-f070lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g140m-f070lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F070LP | G140M | 
| [calib_g140m-f100lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g140m-f100lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F100LP | G140M | 
| [calib_g235h-f170lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g235h-f170lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F170LP | G235H | 
| [calib_g235m-f170lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g235m-f170lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F170LP | G235M | 
| [calib_g395h-f290lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g395h-f290lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F290LP | G395H | 
| [calib_g395m-f290lp_iras-05248-7007_s200a1.v1.spec.fits.gz]({{ site.baseurl }}/data/nirspec-wavecal/calib_g395m-f290lp_iras-05248-7007_s200a1.v1.spec.fits.gz) |  F290LP | G395M | 
| [calib_prism-clear_iras-05248-7007_s200a1.v1.spec.fits.gz ]({{ site.baseurl }}/data/nirspec-wavecal/calib_prism-clear_iras-05248-7007_s200a1.v1.spec.fits.gz ) |  CLEAR  | PRISM | 

### Plots

Notebook: [plot-wavecal-spectra.ipynb]({{ site.baseurl }}/data/nirspec-wavecal/plot-wavecal-spectra.ipynb)

<div class="image fit caption">
    <img src="{{site.baseurl}}/data/nirspec-wavecal/smp58_nirspec_full.png" alt="smp58 full spectrum">

    Full wavelength range

</div>

<div class="image fit caption">
    <img src="{{site.baseurl}}/data/nirspec-wavecal/smp58_nirspec_zoom.png" alt="smp58 zoomed wavelength range">
    
    Zoomed wavelength ranges

</div>

<div class="image fit caption">
    <img src="{{site.baseurl}}/data/nirspec-wavecal/smp58_nirspec_dv.png" alt="smp58 radial velocity">
    
    Show the 294 km/s radial velocity shift
    
</div>
