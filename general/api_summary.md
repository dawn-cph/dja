---
layout: page
title: API tools
showGeneral: true
navigation_weight: 20
---

There are a number of tools provided at [https://grizli-cutout.herokuapp.com/](https://grizli-cutout.herokuapp.com/) for interacting with the DJA database, for example, making image thumbnails and querying for processed exposures that touch a particular sky location.

In general, query centers can be specified either as decimal degrees or HMSDMS sexagesimal strings, either with separate *?ra=&dec=* parameters or with *coords=0.000,0.000* and with the latter separated by either a comma or whitespace, e.g.,

| *thumb?ra=34.4048289&dec=-5.22487* | *thumb?coords=34.4048289,-5.22487* | *thumb?coords=02:17:37.158936,-05:13:29.53* | *thumb?coords=02:17:37.158936 -05:13:29.53* |

# Imaging

The DJA provides reduced *Hubble* and JWST imaging data from many observing programs covering many different fields, from rich survey fields like COSMOS to individual pointings on targeted sources.  Quick access to the imaging metadata is necessary for many different analysis applications.

## Association metadata

DJA defines its own exposure associations essentially split by *program*, *epoch*, *instrument*, *filter*, *detector*, and these associations are the basic processing unit of the imaging data analysis.  That is, the assocation exposures are aligned relative to one-another and to an external astrometric reference, multiple overlapping exposures are used to identify additional bad pixels and cosmic rays, etc.  The JWST association queries are generally specified manually, so not every existing observation is necessarily in the DJA database.  Furthermore, while an association may be *defined*, it may not necessarily have been processed, e.g., for proprietary data.  Associations with *status=2* in the query results below have generally been processed successfully.

The API query [assoc?ra=34.405&dec=-5.22487&arcmin=1](https://grizli-cutout.herokuapp.com/assoc?ra=34.405&dec=-5.22487&arcmin=1) returns a table of metadata for associations close to a specified position within a specified tolerance.  The default returns a readable HTML table.  

Specifying [...&output=csv](https://grizli-cutout.herokuapp.com/assoc?ra=34.405&dec=-5.22487&arcmin=1&output=csv) returns tabular data that can be read directly with, e.g., ``astropy`` or ``pandas``:

|assoc_name                      |target |proposal_id|proposal_pi     |filter     |instrument_name|status|
|--------------------------------|-------|-----------|----------------|-----------|---------------|------|
|j021728m0514_unknown-f090w_00508|unknown|1837       |Dunlop, James S.|F090W-CLEAR|NIRCAM         |2     |
|j021728m0514_unknown-f090w_00511|unknown|1837       |Dunlop, James S.|F090W-CLEAR|NIRCAM         |2     |
| ... | | | | | | |

Specifying [...&output=figure](https://grizli-cutout.herokuapp.com/assoc?ra=34.405&dec=-5.22487&arcmin=1&output=figure) returns a PNG figure:

|  *output=figure* | *&polygon=rect(34.405,-5.22487,1)* | *&instruments=NIRCAM&filters=F200W-CLEAR,F444W-CLEAR* |
| <img src="https://grizli-cutout.herokuapp.com/assoc?ra=34.405&dec=-5.22487&arcmin=1&output=figure" height=300px> | <img src="https://grizli-cutout.herokuapp.com/assoc?output=figure&polygon=rect(34.405,-5.22487,1)" height=300px> | <img src="https://grizli-cutout.herokuapp.com/assoc?output=figure&polygon=rect(34.405,-5.22487,1)&instruments=NIRCAM&filters=F200W-CLEAR,F444W-CLEAR" height=300px> |


## Exposure metadata

The positions of the data in the associations database are taken directly from the MAST metadata for a particular dataset.  Similar to querying the association metadata, it is also possible to perform direct spatial queries using the explicit footprints of discrete *exposures* in the database.  This is more precise for answering a specific question like, "what is the total F090W-CLEAR exposure time at position (34.405,-5.22487)?".

The [exposures?ra=34.405&dec=-5.22487&arcmin=1](https://grizli-cutout.herokuapp.com/exposures?ra=34.405&dec=-5.22487) API query has many of the same functionality as the **assoc** query.  By default the result is a list of individual exposures that include the specified position.

Here the default is machine-readable CSV (below) and [&output=table](https://grizli-cutout.herokuapp.com/exposures?ra=34.405&dec=-5.22487&output=table&filters=F090W-CLEAR) provides a more readable HTML table.

|file                           |extension|dataset                        |assoc                           |parent                                  |filter     |pupil|mdrizsky  |exptime|expstart |sciext|instrume|detector|ndq   |expflag|sunangle|gsky101|gsky102|gsky103|persnpix|perslevl|naxis1|naxis2|crpix1|crpix2|crval1   |crval2    |cd11          |cd12        |cd21        |cd22         |ra1      |dec1      |ra2      |dec2      |ra3      |dec3     |ra4      |dec4      |footprint                                                                                 |modtime  |chipsky|eid    |
|-------------------------------|---------|-------------------------------|--------------------------------|----------------------------------------|-----------|-----|----------|-------|---------|------|--------|--------|------|-------|--------|-------|-------|-------|--------|--------|------|------|------|------|---------|----------|--------------|------------|------------|-------------|---------|----------|---------|----------|---------|---------|---------|----------|------------------------------------------------------------------------------------------|---------|-------|-------|
|jw01837001007_02201_00001_nrcb1|rate     |jw01837001007_02201_00001_nrcb1|j021728m0514_unknown-f090w_00465|uds-01-01837-001-070.0-nrcb1-f090w-clear|F090W-CLEAR|CLEAR|0.32197094|418.734|59965.105|1     |NIRCAM  |NRCB1   |257249|       |        |       |       |       |        |        |2048  |2048  |1025  |1025  |34.402508|-5.2249775|-2.8594375e-06|8.053263e-06|8.03233e-06 |2.8784934e-06|34.397167|-5.236191 |34.41372 |-5.2301984|34.407852|-5.21384 |34.391273|-5.21964  |((34.397167,-5.236191),(34.41372,-5.2301984),(34.407852,-5.21384),(34.391273,-5.21964))   |60788.465|0.0    |442124 |
|jw01837001007_02201_00002_nrcb1|rate     |jw01837001007_02201_00002_nrcb1|j021728m0514_unknown-f090w_00465|uds-01-01837-001-070.0-nrcb1-f090w-clear|F090W-CLEAR|CLEAR|0.311727  |418.734|59965.113|1     |NIRCAM  |NRCB1   |253628|       |        |       |       |       |        |        |2048  |2048  |1025  |1025  |34.402527|-5.2254634|-2.8594131e-06|8.053271e-06|8.032338e-06|2.878469e-06 |34.39719 |-5.2366767|34.41374 |-5.2306843|34.40787 |-5.214326|34.391296|-5.2201257|((34.39719,-5.2366767),(34.41374,-5.2306843),(34.40787,-5.214326),(34.391296,-5.2201257)) |60788.465|0.0    |442127 |
|jw01837001006_02201_00001_nrcb3|rate     |jw01837001006_02201_00001_nrcb3|j021744m0514_unknown-f090w_00255|uds-01-01837-001-070.0-nrcb3-f090w-clear|F090W-CLEAR|CLEAR|0.29258573|418.734|59960.547|1     |NIRCAM  |NRCB3   |243413|       |        |       |       |       |        |        |2048  |2048  |1025  |1025  |34.403687|-5.222797 |-2.9873136e-06|8.044516e-06|8.024133e-06|3.001397e-06 |34.398487|-5.2341566|34.415043|-5.2279024|34.40889 |-5.21157 |34.39235 |-5.2176137|((34.398487,-5.2341566),(34.415043,-5.2279024),(34.40889,-5.21157),(34.39235,-5.2176137)) |60788.535|0.0    |444502 |
|jw01837001006_02201_00002_nrcb3|rate     |jw01837001006_02201_00002_nrcb3|j021744m0514_unknown-f090w_00255|uds-01-01837-001-070.0-nrcb3-f090w-clear|F090W-CLEAR|CLEAR|0.28149673|418.734|59960.555|1     |NIRCAM  |NRCB3   |250973|       |        |       |       |       |        |        |2048  |2048  |1025  |1025  |34.403706|-5.2232804|-2.9872867e-06|8.044526e-06|8.024143e-06|3.00137e-06  |34.398506|-5.2346406|34.415066|-5.2283864|34.40891 |-5.212054|34.392372|-5.218097 |((34.398506,-5.2346406),(34.415066,-5.2283864),(34.40891,-5.212054),(34.392372,-5.218097))|60788.535|0.0    |444507 |

Figure output:

|  *output=figure* | *&polygon=rect(34.405,-5.22487,1)* | *&instruments=NIRCAM&filters=F200W-CLEAR,F444W-CLEAR* |
| <img src="https://grizli-cutout.herokuapp.com/exposures?ra=34.405&dec=-5.22487&arcmin=1&output=figure" height=300px> | <img src="https://grizli-cutout.herokuapp.com/exposures?output=figure&polygon=rect(34.405,-5.22487,1)" height=300px> | <img src="https://grizli-cutout.herokuapp.com/exposures?output=figure&polygon=rect(34.405,-5.22487,1)&instruments=NIRCAM&filters=F200W-CLEAR,F444W-CLEAR" height=300px> |


## Processed data by epoch

The [assoc_mosaic](https://grizli-cutout.herokuapp.com/assoc_mosaic?coords=34.405,-5.22487,1,1&output=figure&filters=F444W-CLEAR&round_epoch=5) tool provides an extension to the **assoc** queries to help identify distinct observing epochs that cover a particular position, e.g., for transient searches.  Note that here only *coords* specification is implemented, as 

- *coords=ra,dec*
- *coords=ra,dec,box_arcmin*
- *coords=ra,dec,width_arcmin,height_arcmin*

| *&filters=F444W-CLEAR&round_epoch=5* | *&filters=F444W-CLEAR&round_epoch=30* (epochs grouped over 30 days) | 
| <img src="https://grizli-cutout.herokuapp.com/assoc_mosaic?coords=34.405,-5.22487,1,1&output=figure&filters=F444W-CLEAR&round_epoch=5" height=300px> | <img src="https://grizli-cutout.herokuapp.com/assoc_mosaic?coords=34.405,-5.22487,1,1&output=figure&filters=F444W-CLEAR&round_epoch=30" height=300px> |

The table outputs include links to sub-mosaics created from the exposures of a particluar association.  The sub-mosaics of the associations at roughly the same part of the sky are drizzled to a common tangent point such that they can be combined or differenced using integer pixel slices without the need for any resampling.  Though not returned in the table, there are inverse variance images available corresponding to each science image that can be retrieved modifying the file URLs *sci.fits.gz* → *wht.fits.gz*.

|file                                                                                                             |assoc_name                      |filter     |modtime            |tile|pixscale_mas|detector|version|status|nexp|visit        |instrument|exptime|expstart|sky |ra       |dec      |t_obs_release     |footprint                                                                                                                                                                                       |dateobs            |preview                                                                                                                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------|--------------------------------|-----------|-------------------|----|------------|--------|-------|------|----|-------------|----------|-------|--------|----|---------|---------|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|[j021744m0514_unknown-f444w_00287-f444w-clear_drc_sci.fits.gz](https://s3.amazonaws.com/grizli-v2/assoc_mosaic/v7.0/j021744m0514_unknown-f444w_00287-f444w-clear_drc_sci.fits.gz)|j021744m0514_unknown-f444w_00287|F444W-CLEAR|2025-04-22 18:05:13|1183|40          |NRCALONG|v7.0   |2     |2   |jw01837001006|NIRCAM    |837.5  |59960.59|0.45|34.407724|-5.263120|59961.297939814816|POLYGON((34.39704,-5.286045),(34.430714,-5.2733455),(34.41859,-5.240085),(34.384377,-5.252073)) POLYGON((34.39706,-5.2865286),(34.430733,-5.273829),(34.41861,-5.2405686),(34.384396,-5.252557))|2023-01-16 14:15:21 | <img src="https://s3.amazonaws.com/grizli-v2/assoc_mosaic/v7.0/j021744m0514_unknown-f444w_00287-f444w-clear_drc_sci.jpg" height=200px> |
|[j021744m0514_unknown-f444w_00291-f444w-clear_drc_sci.fits.gz](https://s3.amazonaws.com/grizli-v2/assoc_mosaic/v7.0/j021744m0514_unknown-f444w_00291-f444w-clear_drc_sci.fits.gz)|j021744m0514_unknown-f444w_00291|F444W-CLEAR|2025-04-22 17:57:14|1183|40          |NRCBLONG|v7.0   |2     |2   |jw01837001006|NIRCAM    |837.5  |59960.59|0.43|34.391558|-5.217158|59961.31527777778 |POLYGON((34.38065,-5.240183),(34.414635,-5.2274103),(34.402393,-5.1941385),(34.368366,-5.206002)) POLYGON((34.38067,-5.240667),(34.414658,-5.227895),(34.402412,-5.1946225),(34.368385,-5.206486))|2023-01-16 14:15:21| <img src="https://s3.amazonaws.com/grizli-v2/assoc_mosaic/v7.0/j021744m0514_unknown-f444w_00291-f444w-clear_drc_sci.jpg" height=200px> | 
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Image cutouts

[https://grizli-cutout.herokuapp.com/thumb?ra=34.4048289&dec=-5.22487](https://grizli-cutout.herokuapp.com/thumb?ra=34.4048289&dec=-5.22487) generates thumbnail cutouts in any HST or JWST dataset that has been processed in the DJA.  The default URL returns images as below, and the options [thumb?output=fits](https://grizli-cutout.herokuapp.com/thumb?output=fits) or [thumb?output=fits_weight](https://grizli-cutout.herokuapp.com/thumb?output=fits_weight) provide FITS cutouts with optional inverse variance WHT extensions.

The monochrome and RGB scaling is generated on the fly with parameters demonstrated below.  The images below are generated from the API itself and may take a bit of time to load if the API VM needs to spin up.

| *default_filters=hst* <br> (f814w,f125w,f160w)  | *thumb?default_filters=jwst* <br> (f115w,f277w,f444w)    | *default_filters=jwst&rgb_min=0.0* <br> (rgb_min black point) |  *default_filters=jwst&asinh=True* <br> (asinh scaling instead of [Lupton 2004](https://ui.adsabs.harvard.edu/abs/2004PASP..116..133L))|
| ![thumb](http://grizli-cutout.herokuapp.com/thumb?default_filters=hst) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?default_filters=jwst) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?default_filters=jwst&rgb_min=0.0) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?default_filters=jwst&asinh=True) | 
| *filters=f090w-clear,f115w-clear,f150w-clear*  | *filters=f090w-clear,f115w-clear,f150w-clear&rgb_scl=1.0,2.0,1.01* |   *filters=f090w-clear,f115w-clear,f150w-clear&pl=1*  |  *filters=f115w-clear,f150w-clear,f200w-clear&pl=1*  | 
| ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f090w-clear,f115w-clear,f150w-clear) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f090w-clear,f115w-clear,f150w-clear&rgb_scl=1.0,2.0,1.01) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f090w-clear,f115w-clear,f150w-clear&pl=1) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f115w-clear,f150w-clear,f200w-clear&pl=1) |
| *filters=f115w-clear&size=2* <br> (default *size=4* arcsec) | *filters=f115w-clear&invert=True*  | *filters=f115w-clear&invert=True&scl=4.0* | *filters=f115w-clear&invert=True&scl=0.2* | 
| ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f115w-clear&size=2) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f115w-clear&invert=True) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f115w-clear&invert=True&scl=4.0) |  ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f115w-clear&invert=True&scl=0.2) |

| *default_filters=jwst&all_filters=True* |
| ![thumb](http://grizli-cutout.herokuapp.com/thumb?default_filters=jwst&all_filters=True) |
| *filters=f090w-clear,f115w-clear,f150w-clear,f200w-clear,f277w-clear,f356w-clear,f444w-clear&all_filters=True&rgb_scl=1.4,0.7,1.2* |
| ![thumb](http://grizli-cutout.herokuapp.com/thumb?filters=f090w-clear,f115w-clear,f150w-clear,f200w-clear,f277w-clear,f356w-clear,f444w-clear&all_filters=True&rgb_scl=1.4,0.7,1.2) |

|  Draw NIRspec slits from the database: <br> *coords=34.2775,-5.2282&nirspec=True* |  Highlight shutters from a particular MSA plan: <br> *nirspec=True&metafile=jw04233001002* | Draw an arbitrary slit (see the image URLs for additional parameters): <br> *thumb?slit={ra},{dec},{length_arcsec},{width_arcsec},{PA}*  | |
| ![thumb](http://grizli-cutout.herokuapp.com/thumb?coords=34.2775,-5.2282&asinh=True&size=2&dpi_scale=2&nirspec=True&nrs_source=magenta&nrs_other=pink&msa_other=lightblue&nrs_lw=1&nrs_alpha=0.5) |  ![thumb](http://grizli-cutout.herokuapp.com/thumb?coords=34.2775,-5.2282&asinh=True&size=2&dpi_scale=2&nirspec=True&metafile=jw04233001002&nrs_source=magenta&nrs_other=pink&msa_other=lightblue&nrs_lw=1&nrs_alpha=0.5) | ![thumb](http://grizli-cutout.herokuapp.com/thumb?slit=34.405,-5.22575,10.0,0.7,15.1&dpi_scale=1) | |

# Spectroscopy

The DJA includes a large and growing compilation of multi-object spectroscopy from NIRSpec.  The [nirspec-merged-table-v4](https://dawn-cph.github.io/dja/blog/2025/05/01/nirspec-merged-table-v4/ post describes the recent large release of ~80,000 NIRspec MSA spectra.  The API provides some functionality for querying the spectroscopy database.

## NIRSpec MSA slits

The last image cutout example above shows how the thumbnails can include an overlay of the NIRSpec MSA shutters that may cover a particluar position.  The shutter footprint data can be retrieved with [nirspec_slits?coords=34.2775,-5.2282&size=1](https://grizli-cutout.herokuapp.com/nirspec_slits?coords=34.2775,-5.2282&size=0.4), where **size** is the query radius in arcsec.

The default output is CSV data:

|program|source_id|ra                |dec                |slitlet_id|shutter_quadrant|shutter_row|shutter_column|estimated_source_in_shutter_x|estimated_source_in_shutter_y|is_source|root                          |footprint                                                                                |exptime|expstart          |grating|filter|msametid|patt_num|msametfl                 |srcra    |srcdec            |valid|
|-------|---------|------------------|-------------------|----------|----------------|-----------|--------------|-----------------------------|-----------------------------|---------|------------------------------|-----------------------------------------------------------------------------------------|-------|------------------|-------|------|--------|--------|-------------------------|---------|------------------|-----|
|4233   |50352    |34.277420265421455|-5.2282717529999445|16        |2               |27         |22            |                             |                             |False    |jw04233001002_03101_00002_nrs1|((34.277424,-5.228348),(34.277364,-5.228322),(34.277417,-5.228196),(34.277477,-5.228221))|948.278|60327.71489975995 |PRISM  |CLEAR |1       |1       |jw04233001002_01_msa.fits|34.277488|-5.228168799999992|True |
|4233   |50352    |34.27747679545152 |-5.2281366726627745|16        |2               |27         |23            |0.164                        |0.333                        |True     |jw04233001002_03101_00002_nrs1|((34.277480,-5.228213),(34.277421,-5.228187),(34.277473,-5.228061),(34.277533,-5.228086))|948.278|60327.71489975995 |PRISM  |CLEAR |1       |1       |jw04233001002_01_msa.fits|34.277488|-5.228168799999992|True |
|4233   |50352    |34.27747796559953 |-5.228136520482815 |16        |2               |27         |22            |0.177                        |0.328                        |True     |jw04233001002_03101_00003_nrs1|((34.277481,-5.228212),(34.277422,-5.228187),(34.277475,-5.228061),(34.277534,-5.228086))|948.278|60327.727056785414|PRISM  |CLEAR |1       |2       |jw04233001002_01_msa.fits|34.277488|-5.228168799999992|True |
|4233   |50352    |34.27741909026612 |-5.228271916974903 |16        |2               |27         |23            |                             |                             |False    |jw04233001002_03101_00004_nrs1|((34.277423,-5.228348),(34.277363,-5.228322),(34.277416,-5.228196),(34.277475,-5.228222))|948.278|60327.73904566273 |PRISM  |CLEAR |1       |3       |jw04233001002_01_msa.fits|34.277488|-5.228168799999992|True |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

The [&count=True&output=json](https://grizli-cutout.herokuapp.com/nirspec_slits?coords=34.2775,-5.2282&count=True&output=json&size=0.4) option returns a summary collated by program and grating (output as CSV or JSON):

```json
{
    "program":{"0":4233,"1":4233},
    "count":{"0":10,"1":10},
    "grating":{"0":"PRISM","1":"G395M"},
    "filter":{"0":"CLEAR","1":"F290LP"}
}
```


## Extracted NIRSpec MSA spectra

If the shutters above correspond to public data that have been processes by the DJA, the spectra themselves can be queried with [nirspec_extractions?coords=34.2775,-5.2282&size=0.4&output=csv](https://grizli-cutout.herokuapp.com/nirspec_extractions?coords=34.2775,-5.2282&size=0.4&output=csv):

|root          |file                                            |ra       |dec               |srcid|msamet                   |slitid|grating     |exptime |wmin      |wmax     |sn50     |flux50  |ctime             |version            |z        |grade|comment                                                         |
|--------------|------------------------------------------------|---------|------------------|-----|-------------------------|------|------------|--------|----------|---------|---------|--------|------------------|-------------------|---------|-----|----------------------------------------------------------------|
|rubies-uds3-v4|rubies-uds3-v4_g395m-f290lp_4233_50352.spec.fits|34.277488|-5.228168799999992|50352|jw04233001003_02_msa.fits|386   |G395M_F290LP|2844.834|2.6851144 |5.499676 |4.7487884|8.550397|1737583244.6615896|0.9.5.dev2+g80b81b4|2.0809047|3    |Redshift matches rubies-uds3-v3_g395m-f290lp_4233_50352 z=2.0814|
|rubies-uds3-v4|rubies-uds3-v4_prism-clear_4233_50352.spec.fits |34.277488|-5.228168799999992|50352|jw04233001003_01_msa.fits|116   |PRISM_CLEAR |2844.834|0.54912597|5.5018334|21.295174|7.581259|1737583241.2015896|0.9.5.dev2+g80b81b4|2.0819318|3    |Redshift matches rubies-uds3-v3_g395m-f290lp_4233_50352 z=2.0814|
|rubies-uds2-v4|rubies-uds2-v4_g395m-f290lp_4233_50352.spec.fits|34.277488|-5.228168799999992|50352|jw04233001002_02_msa.fits|227   |G395M_F290LP|2844.834|2.6851144 |5.499676 |7.295592 |9.274794|1737583707.4645975|0.9.5.dev2+g80b81b4|2.0809047|3    |Redshift matches rubies-uds3-v3_g395m-f290lp_4233_50352 z=2.0814|
|rubies-uds2-v4|rubies-uds2-v4_prism-clear_4233_50352.spec.fits |34.277488|-5.228168799999992|50352|jw04233001002_01_msa.fits|16    |PRISM_CLEAR |2844.834|0.54912597|5.5018334|25.506578|7.736495|1737583704.6445975|0.9.5.dev2+g80b81b4|2.0776203|3    |Redshift matches rubies-uds3-v3_g395m-f290lp_4233_50352 z=2.0814|

The [nirspec_extractions?...&output=html](https://grizli-cutout.herokuapp.com/nirspec_extractions?coords=34.2775,-5.2282&size=0.4&output=html) option gives a human-readable table that also includes the spectrum preview images and links to download the spectrum FITS files.  The locations of the preview images and FITS products have the filename patterns below, where **prefix** is the part of **file** before the ".spec.fits" extension.

| Pattern | Product |
|:---:|:---:|
| https://s3.amazonaws.com/msaexp-nirspec/extractions/**{root}**/**{file}** | [rubies-uds3-v4_prism-clear_4233_50352.spec.fits](https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds3-v4/rubies-uds3-v4_prism-clear_4233_50352.spec.fits) |
| https://s3.amazonaws.com/msaexp-nirspec/extractions/**{root}**/**{prefix}**.fnu.png  | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds3-v4/rubies-uds3-v4_prism-clear_4233_50352.fnu.png" height=200px>  |
| https://s3.amazonaws.com/msaexp-nirspec/extractions/**{root}**/**{prefix}**.flam.png | <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds3-v4/rubies-uds3-v4_prism-clear_4233_50352.flam.png" height=200px> | 


## Individual MSA spectrum redshifts

The [nirspec_file_redshift?file=...](https://grizli-cutout.herokuapp.com/nirspec_file_redshift?file=rubies-uds3-v4_prism-clear_4233_50352.spec.fits) query gives a summary of the redshift estimate associated with a particular spectrum:

|ra               |dec               |zmin_prism|zmax_prism|z_prism   |N_prism|zref_prism|file_prism                                     |zmin_grating|zmax_grating|z_grating|N_grating|zref_grating|file_grating                                    |z        |v_prism|v_grating|root_prism|root_grating|ztype|objid |file                                           |
|-----------------|------------------|----------|----------|----------|-------|----------|-----------------------------------------------|------------|------------|---------|---------|------------|------------------------------------------------|---------|-------|---------|----------|------------|-----|------|-----------------------------------------------|
|34.277488|-5.2281688|2.0776203 |2.0819318 |2.07977605|2      |2.0776203 |rubies-uds2-v4_prism-clear_4233_50352.spec.fits|2.0809047   |2.0809047   |2.0809047|2        |2.0809047   |rubies-uds2-v4_g395m-f290lp_4233_50352.spec.fits|2.0809047|v4     |v4       |          |            |G    |150845|rubies-uds3-v4_prism-clear_4233_50352.spec.fits|

The redshifts are populated based on the table merging potentially multiple observations of a unique source.  These may be more reliable than the redshift fits for the spectrum itself, e.g., where there are no strong features in a particular spectrum but where another spectrum of the same source (e.g., deeper or in a different grating) better constrains the redshift.

## MSA trace overlaps

Some MSA programs such as RUBIES (GO-4233) explicitly allow overlapping grating spectra, which can result in ambiguous contamination and line identifications.  The [/nirspec_trace_overlap?spec_file=rubies-uds3-v4_prism-clear_4233_50352.spec.fits](https://grizli-cutout.herokuapp.com/nirspec_trace_overlap?spec_file=rubies-uds3-v4_prism-clear_4233_50352.spec.fits&exposure=2) API query provides some diagnostics of traces that may overlap with the one of interest.  The default query returns a figure of the traces that may overlap with the primary object associated with the file:

<img src="https://grizli-cutout.herokuapp.com/nirspec_trace_overlap?spec_file=rubies-uds3-v4_g395m-f290lp_4233_50352.spec.fits&exposure=2" height=300px>

The primary trace is shown in black and the overlaps are shown in the curved colored lines. (The example is from RUBIES, which potentially allows a lot of overlaps!).

The overlap data can be retrieved programmatically with [&output=json](https://grizli-cutout.herokuapp.com/nirspec_trace_overlap?spec_file=rubies-uds3-v4_g395m-f290lp_4233_50352.spec.fits&exposure=2&output=json):

```json
{
    "spec_file": "rubies-uds3-v4_prism-clear_4233_50352.spec.fits",
    "yoffset": {
        "4233_49731": 25.009008473508857
        "4233_52910": 13.180923825151922
        "4233_44376": 12.905045711645016
        "4233_51139": 9.516967793545064
        "4233_47720": 5.294313204489072
        "4233_48507": -14.63311231132775
        "4233_46885": -15.269179055199402
        "4233_46566": -15.537329521182642
        "4233_45469": -26.484612871712784
        "4233_46145": -25.87319624823249
        "4233_45210": -31.936282457944003
    }
}
```

The closest trace to that of the primary source (*4233_50352*) is *4233_47720*, about 5 pixels ~ 1 shutter away.  Source *4233_47720* is significantly fainter than *4233_50352*, and indeed there is an apparent signature of the latter contaminating the fainter source in its own diagnostic figure:

| <img src="https://s3.amazonaws.com/msaexp-nirspec/extractions/rubies-uds3-v4/rubies-uds3-v4_g395m-f290lp_4233_47720.fnu.png" height=200px> | <img src="https://grizli-cutout.herokuapp.com/nirspec_trace_overlap?spec_file=rubies-uds3-v4_g395m-f290lp_4233_47720.spec.fits&exposure=2" height=200px> |


## Legacy MOSFIRE spectra

Much of the archival MOSFIRE data were processed prior to JWST launch and are available within the DJA interface.  These have not been revisited much since the advent of the rich JWST spectra, but the processed MOSFIRE reductions can be queried with the [mosfire?](https://grizli-cutout.herokuapp.com/mosfire?mode=table&sep=5&ra=34.4048762&dec=-5.2248069) tool.  The output isn't as well developed as the other queries above, but a JSON version of the query data can be retrieved with [mosfire?...&mode=json](https://grizli-cutout.herokuapp.com/mosfire?mode=json&sep=5&ra=34.4048762&dec=-5.2248069):

```json
[
    {
        "ra_targ": 34.405167,
        "dec_targ": -5.224939,
        "datemask": "UDS_field_new4_20160128",
        "progpi": "mosfireeng",
        "target_name": "lensed_target",
        "filter": "H",
        "wmin": 14616.5,
        "wmax": 17898.85,
        "exptime": 7157.6,
        "file": "UDS_field_new4_20160128/Reduced/UDS_field_new4/2016jan28/H/UDS_field_new4_20160128-H-slit_12-lensed_target_sp.fits",
        "slit_width": 0.7,
        "slit_length": 15.1,
        "skypa3": 10.0,
        "ra_slit": 34.405,
        "dec_slit": -5.22575
    },
    {
        "ra_targ": 34.405167,
        "dec_targ": -5.224236,
        "datemask": "UDSK1_20160118",
        "progpi": "Scoville",
        "target_name": "DM_uds_9612",
        "filter": "K",
        "wmin": 19681.02,
        "wmax": 24050.97,
        "exptime": 2147.3,
        "file": "UDSK1_20160118/Reduced/UDSK1/2016jan18/K/UDSK1_20160118-K-slit_13-DM_uds_9612_sp.fits",
        "slit_width": 0.7,
        "slit_length": 22.8,
        "skypa3": 39.0,
        "ra_slit": 34.403875,
        "dec_slit": -5.225817
    }
 ]
```

The *file* entries listed there are available at *https://s3.amazonaws.com/mosfire-pipeline/Spectra/**{file}***.
 