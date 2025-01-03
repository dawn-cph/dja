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

- [nirspec_graded_v3.html](https://s3.amazonaws.com/msaexp-nirspec/extractions/nirspec_graded_v3.html): Searchable table of all public spectra reduced so far
- For pannable images with various possible layers, including HST and JWST filters as well as spectral observations, see the [Map View]({{ site.baseurl }}/general/mapview/) pages. To see individual spectra, pan over a source with the different *Spectra* overlays enabled.
- See the [nirspec-data-products]({{ site.baseurl }}/blog/2023/07/18/nirspec-data-products/) post for examples on working directly with the catalog and individual extracted spectra

> More documentation coming soon. The spectroscopy reduction process is described in
> [de Graaff et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240905948D/abstract) and 
> [Heintz et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023arXiv230600647H/abstract) 
> and those should be cited if you use the DJA NIRSpec data products, along with any relevant citations to the separate surveys and program IDs for specific spectra.
> The [msaexp](https://github.com/gbrammer/msaexp) software used to process the
> spectra is freely available.

## Public NIRSpec datasets (v3)

These are the public datasets in the [nirspec_graded_v3.html](https://s3.amazonaws.com/msaexp-nirspec/extractions/nirspec_graded_v3.html) compilation:

|  JWST program |  Survey       |   ``root``    | Grating-Filter (t) | *N* total  | *N* ``grade=3``  |
|:-------------:|:-------------:|--------------:|-------------------:|-----------:|-----------------:|
| [1180](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1180&observatory=JWST) |  JADES <br> [D'Eugenio et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240406531D)  |  jades-gds-wide-v3 <br> jades-gds-wide2-v3 <br> jades-gds-wide3-v3 | G140M-F070LP ( 1.7) <br> G235M-F170LP ( 1.7) <br> G395M-F290LP ( 1.7) <br> PRISM-CLEAR ( 1.0) | 1255 | 669 |
| [1181](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1181&observatory=JWST) |  JADES |  jades-gdn-v3 <br> jades-gdn09-v3 <br> jades-gdn10-v3 <br> jades-gdn11-v3 <br> jades-gdn2-blue-v3 <br> jades-gdn2-v3 | G140M-F070LP ( 1.7) <br> G140M-F100LP ( 1.7) <br> G235M-F170LP ( 1.7) <br> G395H-F290LP ( 1.7) <br> G395M-F290LP ( 1.7) <br> PRISM-CLEAR ( 1.7) | 1717 | 1154 |
| [1199](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1199&observatory=JWST) |  GTO [Stiavelli et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...957L..18S) |  macs1149-stiavelli-v3 | G235M-F170LP ( 6.2) <br> G395M-F290LP ( 6.9) | 294 | 77 |
| [1207](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1207&observatory=JWST) |  GTO (G. Rieke) |  gds-rieke-v3 | G140M-F100LP ( 1.9) <br> G235M-F170LP ( 1.9) | 168 | 137 |
| [1210](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1210&observatory=JWST) |  JADES |  gds-deep-v3 | G140M-F070LP ( 4.6) <br> G235M-F170LP ( 4.6) <br> G395H-F290LP ( 4.6) <br> G395M-F290LP ( 4.6) <br> PRISM-CLEAR (18.5) | 217 | 166 |
| [1211](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1211&observatory=JWST) |  GTO WIDE <br> [Maseda et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024A%26A...689A..73M) |  goodsn-wide-v3 <br> goodsn-wide0-v3 <br> goodsn-wide1-v3 <br> goodsn-wide2-v3 <br> goodsn-wide3-v3 <br> goodsn-wide6-v3 <br> goodsn-wide7-v3 <br> goodsn-wide8-v3 | G235H-F170LP ( 0.9) <br> G395H-F290LP ( 1.0) <br> PRISM-CLEAR ( 0.7) | 1115 | 753 |
| [1212](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1212&observatory=JWST) |  GTO WIDE |  jades-gds-w03-v3 <br> jades-gds-w05-v3 <br> jades-gds-w06-v3 <br> jades-gds-w07-v3 <br> jades-gds-w08-v3 <br> jades-gds-w09-v3 | G140M-F100LP ( 0.7) <br> G235H-F170LP ( 0.9) <br> G395H-F290LP ( 1.0) <br> PRISM-CLEAR ( 0.7) | 1119 | 514 |
| [1213](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1213&observatory=JWST) |  GTO WIDE |  gto-wide-egs1-v3 <br> gto-wide-egs2-v3 | G235H-F170LP ( 0.9) <br> G395H-F290LP ( 1.0) <br> PRISM-CLEAR ( 0.7) | 739 | 434 |
| [1214](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1214&observatory=JWST) |  GTO WIDE |  gto-wide-cos01-v3 <br> gto-wide-cos02-v3 <br> gto-wide-cos03-v3 <br> gto-wide-cos05-v3 | G235H-F170LP ( 0.9) <br> G395H-F290LP ( 1.0) <br> PRISM-CLEAR ( 0.7) | 479 | 343 |
| [1215](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1215&observatory=JWST) |  GTO WIDE |  gto-wide-uds10-v3 <br> gto-wide-uds11-v3 <br> gto-wide-uds12-v3 <br> gto-wide-uds13-v3 <br> gto-wide-uds14-v3 | G235H-F170LP ( 0.9) <br> G395H-F290LP ( 1.0) <br> PRISM-CLEAR ( 0.7) | 645 | 431 |
| [1286](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1286&observatory=JWST) |  JADES |  jades-gds05-v3 <br> jades-gds1-v3 | G140M-F070LP ( 2.2) <br> G235M-F170LP ( 2.6) <br> G395H-F290LP ( 2.4) <br> G395M-F290LP ( 2.6) <br> PRISM-CLEAR ( 1.6) | 526 | 211 |
| [1324](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1324&observatory=JWST) |  GLASS-ERS <br> [Mascia et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024A%26A...690A...2M/abstract) |  abell2744-glass-v3 | G140H-F100LP ( 9.7) <br> G235H-F170LP ( 9.7) <br> G395H-F290LP ( 9.7) | 182 | 79 |
| [1345](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1345&observatory=JWST) |  CEERS-ERS <br> [Finkelstein et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...946L..13F) |  ceers-v3 | G140M-F100LP ( 1.7) <br> G235M-F170LP ( 0.9) <br> G395M-F290LP ( 0.9) <br> PRISM-CLEAR ( 0.9) | 1184 | 747 |
| [1433](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1433&observatory=JWST) |  MACS-J0647 <br> [Hsiao et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...973....8H)  |  macsj0647-single-v3 <br> macsj0647-v3 | PRISM-CLEAR ( 1.8) | 226 | 90 |
| [4246](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4246&observatory=JWST) |   |  macsj0647-hr-v3 | G395H-F290LP ( 1.9) | 134 | 44 |
| [1747](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1747&observatory=JWST) |  BoRG |  borg-0037m3337-v3 <br> borg-0314m6712-v3 <br> borg-0409m5317-v3 <br> borg-0440m5244-v3 <br> borg-0859p4114-v3 <br> borg-0955p4528-v3 <br> borg-1033p5051-v3 <br> borg-1437p5044-v3 <br> borg-2203p1851-v3 | PRISM-CLEAR ( 0.7) | 404 | 199 |
| [1810](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1810&observatory=JWST) |  Bluejay <br> [Belli et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024Natur.630...54B) |  bluejay-north-v3 <br> bluejay-south-v3 | G140M-F100LP (25.9) <br> G235M-F170LP ( 6.5) <br> G395M-F290LP ( 1.6) | 140 | 132 |
| [1869](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1869&observatory=JWST) |  LyC-22 |  lyc22-schaerer-03-v3 <br> lyc22-schaerer-12-v3 | G140M-F100LP (18.2) <br> G235M-F170LP (14.6) | 92 | 76 |
| [1871](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1871&observatory=JWST) |   |  gdn-chisholm-v3 | G235H-F170LP (29.2) <br> G395H-F290LP ( 5.3) | 22 | 12 |
| [1879](https://www.stsci.edu/cgi-bin/get-proposal-info?id=1879&observatory=JWST) |   |  cosmos-curti-v3 | G140M-F100LP (30.8) <br> G235H-F170LP ( 5.8) <br> G235M-F170LP ( 7.3) | 75 | 69 |
| [2028](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2028&observatory=JWST) |   |  j0910-wang-v3 | G395M-F290LP ( 3.6) <br> PRISM-CLEAR ( 1.1) | 264 | 114 |
| [2073](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2073&observatory=JWST) |   |  j0252m0503-hennawi-07-v3 <br> j1007p2115-hennawi-v3 | PRISM-CLEAR ( 1.3) | 434 | 161 |
| [2110](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2110&observatory=JWST) |  SUSPENSE <br> [Slob et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...973..131S) |  suspense-kriek-v3 | G140M-F100LP (16.2) | 43 | 39 |
| [2198](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2198&observatory=JWST) |  [Barrufet et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240408052B)  |  gds-barrufet-s156-v3 <br> gds-barrufet-s67-v3 | PRISM-CLEAR ( 0.7) | 139 | 130 |
| [2282](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2282&observatory=JWST) |  [Bradley et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...955...13B)  |  whl0137-v3 | PRISM-CLEAR ( 1.0) | 214 | 59 |
| [2478](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2478&observatory=JWST) |   |  stark-a1703-v3 <br> stark-rxcj2248-v3 | G140M-F100LP ( 3.4) <br> G235M-F170LP ( 0.9) <br> G395M-F290LP ( 0.9) | 94 | 18 |
| [2561](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2561&observatory=JWST) |  UNCOVER <br> [Bezanson et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...974...92B) |  uncover-61-v3 <br> uncover-62-v3 <br> uncover-v3 | PRISM-CLEAR ( 4.4) | 858 | 569 |
| [2565](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2565&observatory=JWST) |  [Nanayakkara et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv241002076N) |  glazebrook-cos-obs1-v3 <br> glazebrook-cos-obs2-v3 <br> glazebrook-cos-obs3-v3 <br> glazebrook-egs-v3 <br> glazebrook-v3 | PRISM-CLEAR ( 0.5) | 631 | 443 |
| [2593](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2593&observatory=JWST) |  CECILIA <br> [Strom et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...958L..11S) |  cecilia-v3 | G235M-F170LP (38.9) <br> G395M-F290LP ( 1.2) | 51 | 30 |
| [2674](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2674&observatory=JWST) |   |  gdn-pah123-v3 <br> gdn-pah4-v3 | G395M-F290LP ( 2.9) | 204 | 105 |
| [2736](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2736&observatory=JWST) |  SMACS-0723 ERO |  smacs0723-ero-v3 | G235M-F170LP ( 9.7) <br> G395M-F290LP ( 9.7) | 62 | 26 |
| [2750](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2750&observatory=JWST) |   [Arrabal Haro et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023Natur.622..707A) |  ceers-ddt-v3 | PRISM-CLEAR ( 5.1) | 154 | 125 |
| [2756](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2756&observatory=JWST) |   |  abell2744-ddt-v3 | PRISM-CLEAR ( 0.6) | 123 | 68 |
| [2767](https://www.stsci.edu/cgi-bin/get-proposal-info?id=2767&observatory=JWST) |   |  rxj2129-ddt-v3 | G140M-F070LP ( 3.3) <br> PRISM-CLEAR ( 1.2) | 145 | 50 |
| [3073](https://www.stsci.edu/cgi-bin/get-proposal-info?id=3073&observatory=JWST) |  [Castellano et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...972..143C)  |  abell2744-castellano1-v3 | PRISM-CLEAR ( 1.8) | 281 | 132 |
| [3215](https://www.stsci.edu/cgi-bin/get-proposal-info?id=3215&observatory=JWST) |  JADES Ultra-Deep <br> [Eisenstein et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023arXiv231012340E)|  gds-udeep-v3 | G140M-F070LP ( 6.9) <br> G395M-F290LP (37.0) <br> PRISM-CLEAR (27.7) | 226 | 145 |
| [4106](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4106&observatory=JWST) |   |  egs-nelsonx-v3 | G395M-F290LP ( 2.2) <br> PRISM-CLEAR ( 3.6) | 136 | 102 |
| [4233](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4233&observatory=JWST) |  RUBIES <br> [de Graaff et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240905948D/abstract) |  rubies-egs51-v3 <br> rubies-egs52-v3 <br> rubies-egs53-v3 <br> rubies-egs61-v3 <br> rubies-egs62-v3 <br> rubies-egs63-v3 <br> rubies-uds1-v3 <br> rubies-uds2-v3 <br> rubies-uds3-v3 <br> rubies-uds31-v3 <br> rubies-uds32-v3 <br> rubies-uds33-v3 <br> rubies-uds41-v3 <br> rubies-uds42-v3 <br> rubies-uds43-v3 | G395M-F290LP ( 0.8) <br> PRISM-CLEAR ( 0.8) | 4158 | 2040 |
| [4446](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4446&observatory=JWST) |   |  snh0pe-v3 | G140M-F100LP ( 2.4) <br> G235M-F170LP ( 3.6) <br> PRISM-CLEAR ( 0.2) | 42 | 24 |
| [4557](https://www.stsci.edu/cgi-bin/get-proposal-info?id=4557&observatory=JWST) |   |  pearls-transients-v3 | PRISM-CLEAR ( 7.8) | 214 | 25 |
| [6541](https://www.stsci.edu/cgi-bin/get-proposal-info?id=6541&observatory=JWST) |   |  gds-egami-ddt-v3 | PRISM-CLEAR ( 2.3) | 339 | 132 |
| [6585](https://www.stsci.edu/cgi-bin/get-proposal-info?id=6585&observatory=JWST) |   |  cosmos-transients-v3 | PRISM-CLEAR ( 3.3) | 300 | 181 |

- The ``root`` column is a general rootname simply indicating spectra that were reduced together.  For many programs that corresponds to individual MSA mask plans (e.g., RUBIES), but for some programs a single ``root`` name can correspond to multiple masks.  For those roots that contain multiple mask plans, all spectra of a particular source from potentially multiple plans were co-added.  This inconsistency of the co-addition treatment is due to the rolling nature of the processing of archival datasets as they became public and may be standardized in future reductions.
- As below, exposure time per spectrum *t* (in hours) computed from `median(exptime)` in the spectra files, which isn't quite correct and double-counts exposure times for spectral extractions that overlap both NRS1 and NRS2 detectors
- "*N* total" is the total number of estimated *unique sources* in that complation.

## Public NIRSpec datasets (v1)
    
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
