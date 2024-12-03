---
layout: page
title: NIRSpec spectra
showSpecDataset: true
navigation_weight: 10
---

<!--span class="image fit"> <img src="{{site.baseurl}}/images/spec_example.png" width="50%" alt="example spectrum"> </span-->

<div class="image fit caption">
    <img src="{{site.baseurl}}/images/gds-deep-lr-v1_prism-clear_1210_58975.fnu.png" alt="example spectrum">

    JADES-DEEP Prism spectrum of GOODS-South #58975
    
</div>

Here you can find various ways to access uniformly-reduced public NIRSpec datasets:

- [nirspec_graded.html](https://s3.amazonaws.com/msaexp-nirspec/extractions/nirspec_graded.html): Searchable table of all public spectra reduced so far
- For pannable images with various possible layers, including HST and JWST filters as well as spectral observations, see the [Map View]({{ site.baseurl }}/general/mapview/) pages. To see individual spectra, pan over a source with the different *Spectra* overlays enabled.
- See the [nirspec-data-products]({{ site.baseurl }}/blog/2023/07/18/nirspec-data-products/) post for examples on working directly with the catalog and individual extracted spectra

> More documentation coming soon. The spectroscopy reduction process is described in
> [de Graaff et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240905948D/abstract) and 
> [Heintz et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023arXiv230600647H/abstract) 
> and those should be cited if you use the DJA NIRSpec data products.
> The [msaexp](https://github.com/gbrammer/msaexp) software used to process the
> spectra is freely available.

## Public NIRSpec datasets
    
These are the public datasets in the [nirspec_graded.html](https://s3.amazonaws.com/msaexp-nirspec/extractions/nirspec_graded.html) compilation:

| ``root`` |  JWST program |  Grating-Filter | *t*, hours | *N* total | *N* ``grade=3``  |
|----------|:-------------:|:---------------:|-----------:|----------:|-----------------:|
| abell2744-ddt-v1     | [2756](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2756&observatory=JWST) | PRISM-CLEAR  |   0.6 |  111 |   51 | 
| abell2744-glass-v1   | [1324](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1324&observatory=JWST) | G140H-F100LP |   6.5 |  179 |   27 | 
| abell2744-glass-v1   | [1324](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1324&observatory=JWST) | G235H-F170LP |   6.5 |  176 |   35 | 
| abell2744-glass-v1   | [1324](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1324&observatory=JWST) | G395H-F290LP |   6.5 |  177 |   31 | 
| ceers-ddt-v1         | [2750](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2750&observatory=JWST) | PRISM-CLEAR  |   5.1 |  266 |  109 | 
| ceers-lr-v1          | [1345](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1345&observatory=JWST) | PRISM-CLEAR  |   0.9 | 1058 |  539 | 
| ceers-mr-v1          | [1345](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1345&observatory=JWST) | G140M-F100LP |   1.7 |  302 |   77 | 
| ceers-mr-v1          | [1345](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1345&observatory=JWST) | G235M-F170LP |   1.7 |  302 |  115 | 
| ceers-mr-v1          | [1345](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1345&observatory=JWST) | G395M-F290LP |   1.7 |  302 |  126 | 
| gds-deep-hr-v1       | [1210](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1210&observatory=JWST) | G395H-F290LP |   4.6 |  154 |   57 | 
| gds-deep-lr-v1       | [1210](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1210&observatory=JWST) | PRISM-CLEAR  |   9.2 |  294 |  159 | 
| gds-deep-mr-v1       | [1210](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1210&observatory=JWST) | G140M-F070LP |   4.6 |  217 |   18 | 
| gds-deep-mr-v1       | [1210](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1210&observatory=JWST) | G235M-F170LP |   4.6 |  216 |   59 | 
| gds-deep-mr-v1       | [1210](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1210&observatory=JWST) | G395M-F290LP |   4.6 |  221 |   68 | 
| goodsn-wide-v1       | [1211](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1211&observatory=JWST) | PRISM-CLEAR  |   0.7 |  182 |   80 | 
| macsj0647-single-v1  | [1433](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1433&observatory=JWST) | PRISM-CLEAR  |   1.8 |   69 |   19 | 
| macsj0647-v1         | [1433](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1433&observatory=JWST) | PRISM-CLEAR  |   1.8 |  132 |   46 | 
| rxj2129-ddt-v1       | [2767](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2767&observatory=JWST) | G140M-F070LP |   2.2 |   20 |    0 | 
| rxj2129-ddt-v1       | [2767](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2767&observatory=JWST) | G140M-F100LP |   2.2 |   20 |    3 | 
| rxj2129-ddt-v1       | [2767](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2767&observatory=JWST) | PRISM-CLEAR  |   1.2 |  103 |   34 | 
| smacs0723-ero-v1     | [2736](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2736&observatory=JWST) | G235M-F170LP |   9.7 |   50 |   12 | 
| smacs0723-ero-v1     | [2736](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2736&observatory=JWST) | G395M-F290LP |   9.7 |   51 |   16 | 
| snH0pe-v1            | [4446](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4446&observatory=JWST) | G140M-F100LP |   2.4 |   39 |   17 | 
| snH0pe-v1            | [4446](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4446&observatory=JWST) | G235M-F170LP |   3.6 |   39 |   15 | 
| snH0pe-v1            | [4446](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4446&observatory=JWST) | PRISM-CLEAR  |   0.2 |   39 |   17 | 
| whl0137-v1           | [2282](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2282&observatory=JWST) | PRISM-CLEAR  |   1.0 |  405 |   80 | 
| *Total*              |              |   |   | 5124 | 1810 | 

- Exposure time per spectrum *t* computed from `median(effexptm)` in the spectra files, which isn't quite correct and double-counts exposure times for spectral extractions that overlap both NRS1 and NRS2 detectors

## Full visualization

<div class="image fit">
    <div class="caption fit">
        1000 NIRSpec prism spectra in one plot!
    </div>
    <img src="{{site.baseurl}}/images/nirspec_prism_compliation_restframe.png" />
</div>

### Spectral coverage comparison

One aspect of the unique power of the NIRSpec PRISM mode is the broad wavelength coverage from 0.7 < &lambda; < 5.3 µm.  The comparisons below show the wavelength coverage from WFC3 G141 slitless spectroscopy or from a ground-based near-infrared spectrograph such as Keck/MOSFIRE with its attendant atmospheric windows.  Note that the comparison just shows the wavelength coverage, not differences in sensitivity and spectral resolution, which are significant between these observing modes.

<div class="image fit">
    <div class="caption fit">
        <button onclick='$("#nirspec_flip").attr("src","{{site.baseurl}}/images/nirspec_prism_compliation_restframe.png");'>NIRSpec</button>
        <button onclick='$("#nirspec_flip").attr("src","{{site.baseurl}}/images/nirspec_prism_compliation_restframe_g141.png");'>WFC3 G141</button>
        <button onclick='$("#nirspec_flip").attr("src","{{site.baseurl}}/images/nirspec_prism_compliation_restframe_mauna_kea.png");'>Ground-based</button>
        
    </div>
    <img src="{{site.baseurl}}/images/nirspec_prism_compliation_restframe.png"         
         alt="spetrum comparison" id="nirspec_flip" />
</div>
