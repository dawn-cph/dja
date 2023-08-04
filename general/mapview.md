---
layout: page
title: Interactive Map Interface
showGeneral: true
navigation_weight: 11
---

<div class="image fit caption">
    <a href="https://s3.amazonaws.com/grizli-v2/ClusterTiles/Map/gds/jwst.html?coord=53.1633772,-27.7705924&zoom=5" target="_blank" rel="noopener noreferrer"> 
        <img src="{{site.baseurl}}/images/map_demo.jpg" alt="map screenshot">
    </a>

    Screenshot of the GOODS-South map viewer, linked to the map itself

 </div>

Fully interactive pannable viewers are available for the fields linked below.  These include overlay layers showing footprints of additional archival datasets (e.g., VLT/MUSE and ALMA from the ESO Archive) and various DJA spectroscopic data products.

### General features 

- The current view of the map is stored and updated in the address bar, providing a link that can be shared, centered on a particular object of interest.
    - (NB: the overlay status is not preserved in the link.)
- Type/paste new coordinates in the text box at lower left ("RA Dec") to recenter the frame without reloading the page.  Both decimal degrees and HH:MM:SS DD:MM:SS sexagesimal coordinate formats allowed.

### Layers & Overlays

- Separate layers for individual filters, as well as the (default) RGB view generated from NIRCam F115W / F277W / F444W.
- *Slits* layers for *all* observed NIRSpec MSA programs, queried through the public ``msametfl`` metadata files.
- *Spectra* layers for the DJA extractions of the public NIRSpec data
- Archival MOSFIRE slits (description TBD)
- VLT/MUSE, ALMA footprints are linked to downloadable datasets from the ESO and ALMA archives, respectively

### Matched links
The links along the bottom of the window offer some queries based on the current center of the frame

- [LegacySurvey](https://www.legacysurvey.org/viewer?layer=ls-dr10&zoom=17&ra=53.1658075&dec=-27.7695593): Similar map view from legacysurveys.org DR10 (centered, but the zooms don't necessarily match)
- [CDS](http://vizier.cds.unistra.fr/viz-bin/VizieR?&-c.rs=2&-c=53.1658075,-27.7695593): Vizier/CDS query within 2" of the center position.  Expand the query with the ``c.rs=2`` parameter in the URL.
- [ESO](https://archive.eso.org/scienceportal/home?pos=53.1658075,-27.7695593&r=0.02&dp_type=IMAGE,CUBE): ESO Archive
- [MOSFIRE](https://grizli-cutout.herokuapp.com/mosfire?mode=table&sep=5&ra=53.1658075&dec=-27.7695593): Query of the DJA MOSFIRE extractions within 5".  Expand the query with the ``sep=5`` keyword in the URL.
- [Cutout](https://grizli-cutout.herokuapp.com/thumb?all_filters=True&size=4&scl=1&asinh=True&filters=f814w,f115w-clear,f150w-clear,f277w-clear,f444w-clear&rgb_scl=1.5,0.84,1.3&pl=2&ra=53.1658075&dec=-27.7695593): Customizable grizli/DJA cutout <br> <span class="image fit"> <a href="https://grizli-cutout.herokuapp.com/thumb?all_filters=True&size=4&scl=1&asinh=True&filters=f814w,f115w-clear,f150w-clear,f277w-clear,f444w-clear&rgb_scl=1.5,0.84,1.3&pl=2&ra=53.1658075&dec=-27.7695593" target="_blank" rel="noopener noreferrer"> <img src="{{site.baseurl}}/images/cutout-qmzznsie-672.rgb.png" alt="cutout option 1"> </a> </span>
- [All NRC](https://grizli-cutout.herokuapp.com/thumb?all_filters=True&size=4&scl=0.5&asinh=False&filters=f814w,f115w-clear,f150w-clear,f200w-clear,f277w-clear,f335w-clear,f356w-clear,f410m-clear,f444w-clear&rgb_scl=1.1,1.05,1.0&pl=2&ra=53.1658075&dec=-27.7695593): another cutout view with additional filters and a different RGB scaling <br> <span class="image fit"> <a href="https://grizli-cutout.herokuapp.com/thumb?all_filters=True&size=4&scl=0.5&asinh=False&filters=f814w,f115w-clear,f150w-clear,f200w-clear,f277w-clear,f335w-clear,f356w-clear,f410m-clear,f444w-clear&rgb_scl=1.1,1.05,1.0&pl=2&ra=53.1658075&dec=-27.7695593" target="_blank" rel="noopener noreferrer"> <img src="{{site.baseurl}}/images/cutout-f1xycda7-672.rgb.png" alt="cutout option 2"> </a> </span>
    - The cutouts preserve the full information needed to regenerate them (coordinates, cutout size, filters, scaling).  The cutout URLs can be pasted into, e.g., Slack, and they will be rendered as images.
    - Some of the cutout options are described at [https://grizli-cutout.herokuapp.com/](https://grizli-cutout.herokuapp.com/).  E.g., to get a FITS cutout rather than the RGB figure, add ``output=fits`` to the URL.
- *MUSE IFU*: VLT/MUSE cutout from the [musewide](https://musewide.aip.de/project/) project (GOODS-South only)


## Fields

{% include components/map_viewers.html %}