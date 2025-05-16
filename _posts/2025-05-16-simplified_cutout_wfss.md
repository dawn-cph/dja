---
layout: post
title:   DJA+Grizli Cutout WFSS spectra
date:   2025-05-16 22:59:38 +0200
categories: spectroscopy
tags: wfss grism demo
author: Gabriel Brammer
showOnHighlights: true
---
{% include components/tags.html %}
# DJA+Grizli Cutout WFSS spectra

Simplified extraction of the grism spectrum for an arbitrary sky position within some WFSS exposure processed with DJA/Grizli.

Totally ignore the full-field contamination model and fit the 2D spectra with flexible spline components to model out continuum / contamination and isolate emission lines.  **No detection image, catalog, segmentation image required!.**

[2025-05-16-simplified_cutout_wfss.ipynb](https://github.com/dawn-cph/dja/blob/master/assets/post_files/2025-05-16-simplified_cutout_wfss.ipynb) Notebook

<a href="https://colab.research.google.com/github/dawn-cph/dja/blob/master/assets/post_files/2025-05-16-simplified_cutout_wfss.ipynb"> <img src="https://colab.research.google.com/assets/colab-badge.svg"> </a>



```python
import os
os.environ['CRDS_CONTEXT'] = "jwst_1322.pmap"
os.environ['NIRCAM_CONF_VERSION'] = "V9"
```

# Build dependencies

E.g., on Google Colab.

Restart runtime if dependencies installed.


```python
try:
    import grizli
except ImportError:
    # Install dependencies - restart runtime if performed
    ! pip install grizli[aws,jwst] msaexp
    ! pip install git+https://github.com/karllark/dust_attenuation.git
```

## Environment variables

Requires an AWS account for downloading exposures, though the functionality shouldn't generate any charges.


```python
import os

env = {
    'CRDS_PATH': '/tmp/crds_cache',
    'CRDS_SERVER_URL': 'https://jwst-crds.stsci.edu'
}
for k in env:
    if os.getenv(k) is None:
        print(f'set {k} = {env[k]}')
        os.environ[k] = env[k]

try:
    from google.colab import userdata
    for k in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
        os.environ[k] = userdata.get(k)
except ImportError:
    pass

if os.getenv('AWS_ACCESS_KEY_ID') is None:
    print('AWS credentials not found.  Set them in the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables')
```

    set CRDS_PATH = /tmp/crds_cache
    set CRDS_SERVER_URL = https://jwst-crds.stsci.edu


## Download config files


```python
from grizli import utils
from grizli.aws import db

CONF_DIR = os.path.join(utils.GRIZLI_PATH, "CONF")
if not os.path.exists(CONF_DIR):
    os.makedirs(CONF_DIR)

utils.fetch_config_files(get_sky=False, get_wfc3=False, get_jwst=True)

if not os.path.exists("fsps_line_templ.fits"):
    db.download_s3_file("s3://grizli-v2/junk/fsps_line_templ.fits")
```

    Set ROOT_PATH=/content
    Config directory: /usr/local/lib/python3.11/dist-packages/grizli/data//CONF
    Get jwst-grism-conf.tar.gz
    Get niriss.conf.220725.tar.gz
    Get WFC3IR_extended_PSF.v1.tar.gz
    Get PSFSTD_WFC3IR_F105W.fits


    WARNING: VerifyWarning: Verification reported errors: [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning: Verification reported errors:
    WARNING: VerifyWarning: HDU 0: [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning: HDU 0:
    WARNING: VerifyWarning:     Card 10: [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning:     Card 10:
    WARNING: VerifyWarning:         Card keyword 'NXPSFs' is not upper case.  Fixed 'NXPSFS' card to meet the FITS standard. [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning:         Card keyword 'NXPSFs' is not upper case.  Fixed 'NXPSFS' card to meet the FITS standard.
    WARNING: VerifyWarning:     Card 11: [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning:     Card 11:
    WARNING: VerifyWarning:         Card keyword 'NYPSFs' is not upper case.  Fixed 'NYPSFS' card to meet the FITS standard. [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning:         Card keyword 'NYPSFs' is not upper case.  Fixed 'NYPSFS' card to meet the FITS standard.
    WARNING: VerifyWarning: Note: astropy.io.fits uses zero-based indexing.
     [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning: Note: astropy.io.fits uses zero-based indexing.
    


    Get PSFSTD_WFC3IR_F125W.fits
    Get PSFSTD_WFC3IR_F140W.fits
    Get PSFSTD_WFC3IR_F160W.fits
    Get PSFSTD_WFC3IR_F110W.fits
    Get PSFSTD_WFC3IR_F127M.fits


    WARNING: VerifyWarning:     Card 12: [astropy.io.fits.verify]
    WARNING:astropy:VerifyWarning:     Card 12:


    Templates directory: /usr/local/lib/python3.11/dist-packages/grizli/data//templates
    Get stars_pickles.npy
    Get stars_bpgs.npy
    ln -s stars_pickles.npy stars.npy
    s3://grizli-v2/junk/fsps_line_templ.fits > ./fsps_line_templ.fits



```python
# GRISM_NIRCAM (N. Pirzkal) for NIRCam
if 1:
    prev = os.getcwd()

    os.chdir(os.path.join(CONF_DIR, 'GRISM_NIRCAM'))

    if not os.path.exists('V9'):
        ! git clone https://github.com/npirzkal/GRISM_NIRCAM.git GRISM_NIRCAM_repo
        ! ln -s GRISM_NIRCAM_repo/* ./
    else:
        print('GRISM_NIRCAM files found')

    os.chdir(prev)
```

    Cloning into 'GRISM_NIRCAM_repo'...
    remote: Enumerating objects: 1491, done.[K
    remote: Counting objects: 100% (353/353), done.[K
    remote: Compressing objects: 100% (194/194), done.[K
    remote: Total 1491 (delta 159), reused 353 (delta 159), pack-reused 1138 (from 1)[K
    Receiving objects: 100% (1491/1491), 219.22 MiB | 2.69 MiB/s, done.
    Resolving deltas: 100% (710/710), done.
    Updating files: 100% (986/986), done.



```python
from grizli import utils, grismconf
grismconf.download_jwst_crds_references()
```

    Use NIRCAM_CONF_VERSION = V9
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_system_datalvl_0002.rmap      694 bytes  (1 / 202 files) (0 / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_system_calver_0046.rmap    5.2 K bytes  (2 / 202 files) (694 / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_system_0045.imap          385 bytes  (3 / 202 files) (5.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_wavelengthrange_0024.rmap    1.4 K bytes  (4 / 202 files) (6.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_wavecorr_0005.rmap      884 bytes  (5 / 202 files) (7.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_superbias_0074.rmap   33.8 K bytes  (6 / 202 files) (8.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_sflat_0026.rmap   20.6 K bytes  (7 / 202 files) (42.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_saturation_0018.rmap    2.0 K bytes  (8 / 202 files) (62.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_refpix_0015.rmap    1.6 K bytes  (9 / 202 files) (64.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_readnoise_0025.rmap    2.6 K bytes  (10 / 202 files) (66.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_photom_0013.rmap      958 bytes  (11 / 202 files) (69.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pathloss_0008.rmap    1.2 K bytes  (12 / 202 files) (70.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-whitelightstep_0001.rmap      777 bytes  (13 / 202 files) (71.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-spec2pipeline_0013.rmap    2.1 K bytes  (14 / 202 files) (72.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-resamplespecstep_0002.rmap      709 bytes  (15 / 202 files) (74.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-outlierdetectionstep_0005.rmap    1.1 K bytes  (16 / 202 files) (74.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-jumpstep_0005.rmap      810 bytes  (17 / 202 files) (76.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-image2pipeline_0008.rmap    1.0 K bytes  (18 / 202 files) (76.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-detector1pipeline_0003.rmap    1.1 K bytes  (19 / 202 files) (77.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-darkpipeline_0003.rmap      872 bytes  (20 / 202 files) (78.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_pars-darkcurrentstep_0001.rmap      622 bytes  (21 / 202 files) (79.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_ote_0030.rmap    1.3 K bytes  (22 / 202 files) (80.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_msaoper_0016.rmap    1.5 K bytes  (23 / 202 files) (81.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_msa_0027.rmap    1.3 K bytes  (24 / 202 files) (83.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_mask_0039.rmap    2.7 K bytes  (25 / 202 files) (84.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_linearity_0017.rmap    1.6 K bytes  (26 / 202 files) (87.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_ipc_0006.rmap      876 bytes  (27 / 202 files) (88.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_ifuslicer_0017.rmap    1.5 K bytes  (28 / 202 files) (89.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_ifupost_0019.rmap    1.5 K bytes  (29 / 202 files) (91.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_ifufore_0017.rmap    1.5 K bytes  (30 / 202 files) (92.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_gain_0023.rmap    1.8 K bytes  (31 / 202 files) (94.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_fpa_0028.rmap    1.3 K bytes  (32 / 202 files) (95.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_fore_0026.rmap    5.0 K bytes  (33 / 202 files) (97.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_flat_0015.rmap    3.8 K bytes  (34 / 202 files) (102.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_fflat_0026.rmap    7.2 K bytes  (35 / 202 files) (105.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_extract1d_0018.rmap    2.3 K bytes  (36 / 202 files) (113.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_disperser_0028.rmap    5.7 K bytes  (37 / 202 files) (115.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_dflat_0007.rmap    1.1 K bytes  (38 / 202 files) (121.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_dark_0069.rmap   32.6 K bytes  (39 / 202 files) (122.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_cubepar_0015.rmap      966 bytes  (40 / 202 files) (154.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_collimator_0026.rmap    1.3 K bytes  (41 / 202 files) (155.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_camera_0026.rmap    1.3 K bytes  (42 / 202 files) (157.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_barshadow_0007.rmap    1.8 K bytes  (43 / 202 files) (158.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_area_0018.rmap    6.3 K bytes  (44 / 202 files) (160.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_apcorr_0009.rmap    5.6 K bytes  (45 / 202 files) (166.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nirspec_0387.imap       5.7 K bytes  (46 / 202 files) (171.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_wfssbkg_0008.rmap    3.1 K bytes  (47 / 202 files) (177.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_wavemap_0008.rmap    2.2 K bytes  (48 / 202 files) (180.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_wavelengthrange_0006.rmap      862 bytes  (49 / 202 files) (183.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_trappars_0004.rmap      753 bytes  (50 / 202 files) (183.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_trapdensity_0005.rmap      705 bytes  (51 / 202 files) (184.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_throughput_0005.rmap    1.3 K bytes  (52 / 202 files) (185.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_superbias_0030.rmap    7.4 K bytes  (53 / 202 files) (186.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_specwcs_0014.rmap    3.1 K bytes  (54 / 202 files) (194.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_spectrace_0008.rmap    2.3 K bytes  (55 / 202 files) (197.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_specprofile_0008.rmap    2.4 K bytes  (56 / 202 files) (199.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_speckernel_0006.rmap    1.0 K bytes  (57 / 202 files) (201.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_saturation_0015.rmap      829 bytes  (58 / 202 files) (202.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_readnoise_0011.rmap      987 bytes  (59 / 202 files) (203.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_photom_0036.rmap    1.3 K bytes  (60 / 202 files) (204.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_persat_0007.rmap      674 bytes  (61 / 202 files) (205.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pathloss_0003.rmap      758 bytes  (62 / 202 files) (206.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pastasoss_0004.rmap      818 bytes  (63 / 202 files) (207.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-undersamplecorrectionstep_0001.rmap      904 bytes  (64 / 202 files) (208.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-tweakregstep_0012.rmap    3.1 K bytes  (65 / 202 files) (209.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-spec2pipeline_0008.rmap      984 bytes  (66 / 202 files) (212.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-sourcecatalogstep_0002.rmap    2.3 K bytes  (67 / 202 files) (213.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-resamplestep_0002.rmap      687 bytes  (68 / 202 files) (215.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-outlierdetectionstep_0004.rmap    2.7 K bytes  (69 / 202 files) (216.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-jumpstep_0007.rmap    6.4 K bytes  (70 / 202 files) (218.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-image2pipeline_0005.rmap    1.0 K bytes  (71 / 202 files) (225.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-detector1pipeline_0002.rmap    1.0 K bytes  (72 / 202 files) (226.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-darkpipeline_0002.rmap      868 bytes  (73 / 202 files) (227.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-darkcurrentstep_0001.rmap      591 bytes  (74 / 202 files) (228.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_pars-chargemigrationstep_0004.rmap    5.7 K bytes  (75 / 202 files) (228.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_nrm_0005.rmap      663 bytes  (76 / 202 files) (234.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_mask_0022.rmap    1.3 K bytes  (77 / 202 files) (235.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_linearity_0022.rmap      961 bytes  (78 / 202 files) (236.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_ipc_0007.rmap      651 bytes  (79 / 202 files) (237.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_gain_0011.rmap      797 bytes  (80 / 202 files) (238.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_flat_0023.rmap    5.9 K bytes  (81 / 202 files) (238.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_filteroffset_0010.rmap      853 bytes  (82 / 202 files) (244.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_extract1d_0007.rmap      905 bytes  (83 / 202 files) (245.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_drizpars_0004.rmap      519 bytes  (84 / 202 files) (246.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_distortion_0025.rmap    3.4 K bytes  (85 / 202 files) (246.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_dark_0034.rmap    7.5 K bytes  (86 / 202 files) (250.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_area_0014.rmap    2.7 K bytes  (87 / 202 files) (257.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_apcorr_0010.rmap    4.3 K bytes  (88 / 202 files) (260.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_abvegaoffset_0004.rmap    1.4 K bytes  (89 / 202 files) (264.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_niriss_0267.imap        5.8 K bytes  (90 / 202 files) (266.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_wfssbkg_0004.rmap    7.2 K bytes  (91 / 202 files) (272.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_wavelengthrange_0010.rmap      996 bytes  (92 / 202 files) (279.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_tsophot_0003.rmap      896 bytes  (93 / 202 files) (280.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_trappars_0003.rmap    1.6 K bytes  (94 / 202 files) (281.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_trapdensity_0003.rmap    1.6 K bytes  (95 / 202 files) (282.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_superbias_0018.rmap   16.2 K bytes  (96 / 202 files) (284.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_specwcs_0022.rmap    7.1 K bytes  (97 / 202 files) (300.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_sirskernel_0002.rmap      671 bytes  (98 / 202 files) (307.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_saturation_0010.rmap    2.2 K bytes  (99 / 202 files) (308.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_readnoise_0025.rmap   23.2 K bytes  (100 / 202 files) (310.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_psfmask_0008.rmap   28.4 K bytes  (101 / 202 files) (333.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_photom_0028.rmap    3.4 K bytes  (102 / 202 files) (362.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_persat_0005.rmap    1.6 K bytes  (103 / 202 files) (365.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-whitelightstep_0003.rmap    1.5 K bytes  (104 / 202 files) (367.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-tweakregstep_0003.rmap    4.5 K bytes  (105 / 202 files) (368.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-spec2pipeline_0008.rmap      984 bytes  (106 / 202 files) (372.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-sourcecatalogstep_0002.rmap    4.6 K bytes  (107 / 202 files) (373.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-resamplestep_0002.rmap      687 bytes  (108 / 202 files) (378.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-outlierdetectionstep_0003.rmap      940 bytes  (109 / 202 files) (379.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-jumpstep_0005.rmap      806 bytes  (110 / 202 files) (380.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-image2pipeline_0003.rmap    1.0 K bytes  (111 / 202 files) (381.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-detector1pipeline_0003.rmap    1.0 K bytes  (112 / 202 files) (382.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-darkpipeline_0002.rmap      868 bytes  (113 / 202 files) (383.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_pars-darkcurrentstep_0001.rmap      618 bytes  (114 / 202 files) (383.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_mask_0011.rmap    3.5 K bytes  (115 / 202 files) (384.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_linearity_0011.rmap    2.4 K bytes  (116 / 202 files) (388.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_ipc_0003.rmap    2.0 K bytes  (117 / 202 files) (390.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_gain_0016.rmap    2.1 K bytes  (118 / 202 files) (392.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_flat_0027.rmap   51.7 K bytes  (119 / 202 files) (394.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_filteroffset_0004.rmap    1.4 K bytes  (120 / 202 files) (446.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_extract1d_0004.rmap      842 bytes  (121 / 202 files) (447.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_drizpars_0001.rmap      519 bytes  (122 / 202 files) (448.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_distortion_0033.rmap   53.4 K bytes  (123 / 202 files) (449.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_dark_0046.rmap   26.4 K bytes  (124 / 202 files) (502.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_area_0012.rmap   33.5 K bytes  (125 / 202 files) (528.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_apcorr_0008.rmap    4.3 K bytes  (126 / 202 files) (562.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_abvegaoffset_0003.rmap    1.3 K bytes  (127 / 202 files) (566.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_nircam_0301.imap        5.6 K bytes  (128 / 202 files) (567.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_wavelengthrange_0027.rmap      929 bytes  (129 / 202 files) (573.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_tsophot_0004.rmap      882 bytes  (130 / 202 files) (574.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_straymask_0009.rmap      987 bytes  (131 / 202 files) (575.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_specwcs_0042.rmap    5.8 K bytes  (132 / 202 files) (576.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_saturation_0015.rmap    1.2 K bytes  (133 / 202 files) (582.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_rscd_0008.rmap     1.0 K bytes  (134 / 202 files) (583.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_resol_0006.rmap      790 bytes  (135 / 202 files) (584.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_reset_0026.rmap    3.9 K bytes  (136 / 202 files) (585.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_regions_0033.rmap    5.2 K bytes  (137 / 202 files) (588.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_readnoise_0023.rmap    1.6 K bytes  (138 / 202 files) (594.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_psfmask_0009.rmap    2.1 K bytes  (139 / 202 files) (595.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_psf_0002.rmap        753 bytes  (140 / 202 files) (597.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_photom_0056.rmap    3.7 K bytes  (141 / 202 files) (598.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pathloss_0005.rmap      866 bytes  (142 / 202 files) (602.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-whitelightstep_0003.rmap      912 bytes  (143 / 202 files) (603.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-tweakregstep_0003.rmap    1.8 K bytes  (144 / 202 files) (604.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-spec3pipeline_0009.rmap      816 bytes  (145 / 202 files) (605.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-spec2pipeline_0012.rmap    1.3 K bytes  (146 / 202 files) (606.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-sourcecatalogstep_0003.rmap    1.9 K bytes  (147 / 202 files) (608.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-resamplestep_0002.rmap      677 bytes  (148 / 202 files) (610.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-resamplespecstep_0002.rmap      706 bytes  (149 / 202 files) (610.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-outlierdetectionstep_0017.rmap    3.4 K bytes  (150 / 202 files) (611.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-jumpstep_0011.rmap    1.6 K bytes  (151 / 202 files) (614.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-image2pipeline_0007.rmap      983 bytes  (152 / 202 files) (616.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-extract1dstep_0003.rmap      807 bytes  (153 / 202 files) (617.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-emicorrstep_0003.rmap      796 bytes  (154 / 202 files) (618.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-detector1pipeline_0010.rmap    1.6 K bytes  (155 / 202 files) (618.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-darkpipeline_0002.rmap      860 bytes  (156 / 202 files) (620.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_pars-darkcurrentstep_0002.rmap      683 bytes  (157 / 202 files) (621.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_mrsxartcorr_0002.rmap    2.2 K bytes  (158 / 202 files) (622.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_mrsptcorr_0005.rmap    2.0 K bytes  (159 / 202 files) (624.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_mask_0023.rmap     3.5 K bytes  (160 / 202 files) (626.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_linearity_0018.rmap    2.8 K bytes  (161 / 202 files) (629.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_ipc_0008.rmap        700 bytes  (162 / 202 files) (632.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_gain_0013.rmap     3.9 K bytes  (163 / 202 files) (633.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_fringefreq_0003.rmap    1.4 K bytes  (164 / 202 files) (637.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_fringe_0019.rmap    3.9 K bytes  (165 / 202 files) (638.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_flat_0065.rmap    15.5 K bytes  (166 / 202 files) (642.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_filteroffset_0025.rmap    2.5 K bytes  (167 / 202 files) (657.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_extract1d_0020.rmap    1.4 K bytes  (168 / 202 files) (660.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_emicorr_0003.rmap      663 bytes  (169 / 202 files) (661.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_drizpars_0002.rmap      511 bytes  (170 / 202 files) (662.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_distortion_0040.rmap    4.9 K bytes  (171 / 202 files) (662.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_dark_0036.rmap     4.4 K bytes  (172 / 202 files) (667.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_cubepar_0017.rmap      800 bytes  (173 / 202 files) (672.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_area_0015.rmap       866 bytes  (174 / 202 files) (673.0 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_apcorr_0019.rmap    5.0 K bytes  (175 / 202 files) (673.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_abvegaoffset_0003.rmap    1.3 K bytes  (176 / 202 files) (678.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_miri_0423.imap          5.8 K bytes  (177 / 202 files) (680.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_trappars_0004.rmap      903 bytes  (178 / 202 files) (685.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_trapdensity_0006.rmap      930 bytes  (179 / 202 files) (686.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_superbias_0017.rmap    3.8 K bytes  (180 / 202 files) (687.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_saturation_0009.rmap      779 bytes  (181 / 202 files) (691.5 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_readnoise_0011.rmap    1.3 K bytes  (182 / 202 files) (692.3 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_photom_0014.rmap    1.1 K bytes  (183 / 202 files) (693.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_persat_0006.rmap      884 bytes  (184 / 202 files) (694.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_pars-tweakregstep_0002.rmap      850 bytes  (185 / 202 files) (695.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_pars-sourcecatalogstep_0001.rmap      636 bytes  (186 / 202 files) (696.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_pars-outlierdetectionstep_0001.rmap      654 bytes  (187 / 202 files) (697.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_pars-image2pipeline_0005.rmap      974 bytes  (188 / 202 files) (697.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_pars-detector1pipeline_0002.rmap    1.0 K bytes  (189 / 202 files) (698.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_pars-darkpipeline_0002.rmap      856 bytes  (190 / 202 files) (699.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_mask_0023.rmap      1.1 K bytes  (191 / 202 files) (700.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_linearity_0015.rmap      925 bytes  (192 / 202 files) (701.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_ipc_0003.rmap         614 bytes  (193 / 202 files) (702.6 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_gain_0010.rmap        890 bytes  (194 / 202 files) (703.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_flat_0009.rmap      1.1 K bytes  (195 / 202 files) (704.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_distortion_0011.rmap    1.2 K bytes  (196 / 202 files) (705.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_dark_0017.rmap      4.3 K bytes  (197 / 202 files) (706.4 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_area_0010.rmap      1.2 K bytes  (198 / 202 files) (710.7 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_apcorr_0004.rmap    4.0 K bytes  (199 / 202 files) (711.9 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_abvegaoffset_0002.rmap    1.3 K bytes  (200 / 202 files) (715.8 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_fgs_0118.imap           5.1 K bytes  (201 / 202 files) (717.1 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/mappings/jwst/jwst_1322.pmap                 580 bytes  (202 / 202 files) (722.2 K / 722.8 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_photom_0162.fits    1.7 M bytes  (1 / 2 files) (0 / 1.7 M bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0186.asdf    9.3 K bytes  (2 / 2 files) (1.7 M / 1.7 M bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_photom_0163.fits    1.7 M bytes  (1 / 2 files) (0 / 1.7 M bytes)


    crds_reffiles: NIRCAM F277W GRISMR A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0186.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0160.asdf    9.3 K bytes  (2 / 2 files) (1.7 M / 1.7 M bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0171.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F277W GRISMR B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0160.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0174.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F277W GRISMC A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0171.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0184.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F277W GRISMC B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0174.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0199.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F356W GRISMR A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0184.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0165.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F356W GRISMR B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0199.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0182.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F356W GRISMC A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0165.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0178.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F356W GRISMC B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0182.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0164.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F410M GRISMR A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0178.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0181.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F410M GRISMR B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0164.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap
    crds_reffiles: NIRCAM F410M GRISMC A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0181.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0159.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0190.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F410M GRISMC B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0159.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap
    crds_reffiles: NIRCAM F444W GRISMR A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0190.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0187.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0173.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F444W GRISMR B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0187.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0203.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F444W GRISMC A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0173.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0191.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F444W GRISMC B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0203.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0179.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F460M GRISMR A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0191.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0195.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F460M GRISMR B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0179.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0169.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F460M GRISMC A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0195.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0192.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F460M GRISMC B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0169.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0197.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F480M GRISMR A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0192.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0180.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F480M GRISMR B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0197.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/nircam/jwst_nircam_specwcs_0168.asdf    9.3 K bytes  (1 / 1 files) (0 / 9.3 K bytes)


    crds_reffiles: NIRCAM F480M GRISMC A (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0162.fits jwst_nircam_specwcs_0180.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap
    crds_reffiles: NIRCAM F480M GRISMC B (jwst_1322.pmap)
    crds_reffiles: jwst_nircam_photom_0163.fits jwst_nircam_specwcs_0168.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_photom_0041.fits    3.6 M bytes  (1 / 2 files) (0 / 3.6 M bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0050.asdf   20.6 K bytes  (2 / 2 files) (3.6 M / 3.6 M bytes)
    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0047.asdf   20.6 K bytes  (1 / 1 files) (0 / 20.6 K bytes)


    crds_reffiles: NIRISS GR150R F090W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0050.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf   24.4 K bytes  (1 / 1 files) (0 / 24.4 K bytes)


    crds_reffiles: NIRISS GR150C F090W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0047.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0053.asdf   27.4 K bytes  (1 / 1 files) (0 / 27.4 K bytes)


    crds_reffiles: NIRISS GR150R F115W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0054.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf   27.5 K bytes  (1 / 1 files) (0 / 27.5 K bytes)


    crds_reffiles: NIRISS GR150C F115W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0053.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0055.asdf   30.5 K bytes  (1 / 1 files) (0 / 30.5 K bytes)


    crds_reffiles: NIRISS GR150R F150W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0056.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf   27.5 K bytes  (1 / 1 files) (0 / 27.5 K bytes)


    crds_reffiles: NIRISS GR150C F150W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0055.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap


    CRDS - INFO -  Fetching  /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0051.asdf   30.5 K bytes  (1 / 1 files) (0 / 30.5 K bytes)


    crds_reffiles: NIRISS GR150R F200W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0052.asdf
    ENV CRDS_CONTEXT = jwst_1322.pmap
    crds_reffiles: NIRISS GR150C F200W A (jwst_1322.pmap)
    crds_reffiles: jwst_niriss_photom_0041.fits jwst_niriss_specwcs_0051.asdf


# Imports

Can skip to here if config files and dependencies already installed above.


```python
import os

import numpy as np
import matplotlib.pyplot as plt

import astropy.io.fits as pyfits
import astropy.wcs as pywcs

import grizli.jwst_utils
grizli.jwst_utils.set_quiet_logging()

from grizli.aws import db
from grizli import utils, grismconf
from grizli.aws import sky_wfss

utils.set_warnings()

import grizli
import msaexp

from IPython.display import Image

print('grizli version: ', grizli.__version__)
print('msaexp version: ', msaexp.__version__)

```

    grizli version:  1.12.14
    msaexp version:  0.9.8



```python
from importlib import reload
reload(sky_wfss)

prefix = 'dja-grism'
kwargs = {}

# Segmentation image for NIRISS demo
if not os.path.exists('gds-sw-grizli-v7.0-ir_seg.fits'):
    ! wget https://s3.amazonaws.com/grizli-v2/JwstMosaics/v7/gds-sw-grizli-v7.0-ir_seg.fits.gz
    ! gunzip gds-sw-grizli-v7.0-ir_seg.fits.gz
```

    --2025-05-16 19:27:21--  https://s3.amazonaws.com/grizli-v2/JwstMosaics/v7/gds-sw-grizli-v7.0-ir_seg.fits.gz
    Resolving s3.amazonaws.com (s3.amazonaws.com)... 3.5.9.70, 54.231.192.120, 16.182.105.32, ...
    Connecting to s3.amazonaws.com (s3.amazonaws.com)|3.5.9.70|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 5996324 (5.7M) [binary/octet-stream]
    Saving to: ‘gds-sw-grizli-v7.0-ir_seg.fits.gz’
    
    gds-sw-grizli-v7.0- 100%[===================>]   5.72M  14.4MB/s    in 0.4s    
    
    2025-05-16 19:27:22 (14.4 MB/s) - ‘gds-sw-grizli-v7.0-ir_seg.fits.gz’ saved [5996324/5996324]
    


# Set source and extract spectrum

All you really need to specify is a set of target coordinates ``(ra, dec)`` and a list of the desired grism names to search for.  

The script
1. Queries and downloads all DJA-processed exposures whose corner footprint contains the requested point.  Note that there might not be a usable spectrum in a particular exposure if the nominal coordinate is within the WCS "footprint" of the grism exposure but the dispersed spectrum falls off of the detector.
2. Pulls a FITS cutout from the DJA/grizli API to use for the direct image.  No direct image is needed for the basic extraction and redshift fitting, which here uses a simplified Gaussian model for the optimal extractions, but the direct image is needed for the full grizli functionality (line maps, etc.)
3. Generates a `grizli.multifit.MultiBeam` object of 2D cutouts from the grism exposures.

## NIRISS

If a `segmentation_image` is provided, the source ID will be read from the specified target coordinates and the segmentation image will be used for a crude zeroth-order mask.


```python
reload(sky_wfss)

## NIRISS test
ra, dec = 53.1666323, -27.8690371 # multiple lines

# segmentation_image = "gds-sw-grizli-v7.0-ir_seg.fits"
segmentation_image = None

mb = sky_wfss.extract_from_coords(
    ra=ra, dec=dec,
    grisms=['F115W-GR150R','F115W-GR150C','F150W-GR150R','F150W-GR150C','F200W-GR150R','F200W-GR150C'][0::2],
    size=24,
    grp=None,
    clean=False,
    get_cutout=1,
    cutout_filter=','.join(['F150W-CLEAR','F150WN-CLEAR','F200W-CLEAR','F200WN-CLEAR'][:]), # Direct image filters
    thumbnail_size=0.8 * 4,
    prefix=prefix,
    mb_kwargs={"min_sens": 0.0, "min_mask": 0.0},
    filter_kwargs=[{}, None][1],
    verbose=True,
    local=False,
    segmentation_image=segmentation_image,
    use_jwst_crds=True,
    **kwargs
)
```

    https://grizli-cutout.herokuapp.com/exposures?polygon=rect(53.166632,-27.869037,0.25)&filters=F115W-GR150R,F150W-GR150R,F200W-GR150R&output=csv
    extract_from_coords: dja-grism_033239.99-275208.53 27 exposures
    ./jw01283005001_04201_00001_nis_rate.fits exists
    ./jw01283005001_04201_00002_nis_rate.fits exists
    ./jw01283005001_04201_00003_nis_rate.fits exists
    ./jw01283005001_04201_00004_nis_rate.fits exists
    ./jw01283005001_04201_00005_nis_rate.fits exists
    ./jw01283005001_04201_00006_nis_rate.fits exists
    ./jw01283005001_04201_00007_nis_rate.fits exists
    ./jw01283005001_04201_00008_nis_rate.fits exists
    ./jw01283005001_04201_00009_nis_rate.fits exists
    ./jw01283005001_09201_00001_nis_rate.fits exists
    ./jw01283005001_09201_00002_nis_rate.fits exists
    ./jw01283005001_09201_00003_nis_rate.fits exists
    ./jw01283005001_09201_00004_nis_rate.fits exists
    ./jw01283005001_09201_00005_nis_rate.fits exists
    ./jw01283005001_09201_00006_nis_rate.fits exists
    ./jw01283005001_09201_00007_nis_rate.fits exists
    ./jw01283005001_09201_00008_nis_rate.fits exists
    ./jw01283005001_09201_00009_nis_rate.fits exists
    ./jw01283005001_14201_00001_nis_rate.fits exists
    ./jw01283005001_14201_00002_nis_rate.fits exists
    ./jw01283005001_14201_00003_nis_rate.fits exists
    ./jw01283005001_14201_00004_nis_rate.fits exists
    ./jw01283005001_14201_00005_nis_rate.fits exists
    ./jw01283005001_14201_00006_nis_rate.fits exists
    ./jw01283005001_14201_00007_nis_rate.fits exists
    ./jw01283005001_14201_00008_nis_rate.fits exists
    ./jw01283005001_14201_00009_nis_rate.fits exists
    https://grizli-cutout.herokuapp.com/thumb?all_filters=False&filters=f150w-clear,f150wn-clear,f200w-clear,f200wn-clear&ra=53.1666323&dec=-27.8690371&size=3.2&output=fits_weight -> dja-grism_033239.99-275208.53_ir.fits
    thumbnail: F150W-CLEAR
    thumbnail: F150WN-CLEAR
    thumbnail: F200W-CLEAR
    thumbnail: F200WN-CLEAR
    extract_from_coords: direct image = dja-grism_033239.99-275208.53_ir.fits
     1 / 27 GroupFLT jw01283005001_04201_00001_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     2 / 27 GroupFLT jw01283005001_04201_00002_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     3 / 27 GroupFLT jw01283005001_04201_00003_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     4 / 27 GroupFLT jw01283005001_04201_00004_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     5 / 27 GroupFLT jw01283005001_04201_00005_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     6 / 27 GroupFLT jw01283005001_04201_00006_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     7 / 27 GroupFLT jw01283005001_04201_00007_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     8 / 27 GroupFLT jw01283005001_04201_00008_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
     9 / 27 GroupFLT jw01283005001_04201_00009_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0054.asdf GR150R F115W F115W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    10 / 27 GroupFLT jw01283005001_09201_00001_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    11 / 27 GroupFLT jw01283005001_09201_00002_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    12 / 27 GroupFLT jw01283005001_09201_00003_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    13 / 27 GroupFLT jw01283005001_09201_00004_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    14 / 27 GroupFLT jw01283005001_09201_00005_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    15 / 27 GroupFLT jw01283005001_09201_00006_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    16 / 27 GroupFLT jw01283005001_09201_00007_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    17 / 27 GroupFLT jw01283005001_09201_00008_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    18 / 27 GroupFLT jw01283005001_09201_00009_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0056.asdf GR150R F150W F150W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    19 / 27 GroupFLT jw01283005001_14201_00001_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    20 / 27 GroupFLT jw01283005001_14201_00002_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    21 / 27 GroupFLT jw01283005001_14201_00003_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    22 / 27 GroupFLT jw01283005001_14201_00004_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    23 / 27 GroupFLT jw01283005001_14201_00005_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    24 / 27 GroupFLT jw01283005001_14201_00006_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    25 / 27 GroupFLT jw01283005001_14201_00007_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    26 / 27 GroupFLT jw01283005001_14201_00008_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    27 / 27 GroupFLT jw01283005001_14201_00009_nis_rate.fits
    get_conf: xxx /tmp/crds_cache/references/jwst/niriss/jwst_niriss_specwcs_0052.asdf GR150R F200W F200W None NIRISS
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    Using default C-based coordinate transformation...
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    extract_from_coords: dja-grism_033239.99-275208.53 27 beam cutouts



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_16_1.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_16_2.png)
    


### Fit redshift

This script tries to fit flexible functions to account for the contamination, and uses a simplified compact Gaussian profile to use for the optimal extraction.  These are crude approximations, but actually tend to work acceptably for emission lines with reasonable S/N.


```python
from importlib import reload
reload(sky_wfss)

dv = 800 # line width for fitting, km/s

b2d, zres = sky_wfss.combine_beams_2d(
    mb,
    step=0.5, pixfrac=0.75, # 2D "pseudodrizzle" parameters
    ymax=12.5,
    profile_sigma=1.5, profile_offset=-0.5, profile_type="gaussian",     # Gaussian cross-dispersion model
    # profile_type="grizli",                                             # Estimate a profile using the direct image
    bkg_percentile=None,
    # cont_spline=11, zfit_nspline=-1,  # Remove all contamination *before* fitting
    cont_spline=0, zfit_nspline=11,     # Fit with flexible splines to model contamination
    zfit_kwargs=dict(
        rest_wave=[6500, 4400], # Halpha - OIII
        velocity_sigma=dv,
        dz=dv/3.e5/2,
    ),
    ylim=(-3, 20), yticks=[0, 5, 10, 20],
    auto_niriss=False,
)

```

    final spectrum file: dja-grism_033239.99-275208.53.f115w.spec.fits
    final spectrum file: dja-grism_033239.99-275208.53.f150w.spec.fits
    final spectrum file: dja-grism_033239.99-275208.53.f200w.spec.fits
    redshift_fit_1d dja-grism_033239.99-275208.53 z=[0.492, 4.226] dz=0.0013333333333333333  nsteps=941
    redshift_fit_1d dja-grism_033239.99-275208.53 best z=1.41168  dlnP=2526.9
    redshift_fit_1d dja-grism_033239.99-275208.53 F115W dlnP=1375.5
    redshift_fit_1d dja-grism_033239.99-275208.53 F150W dlnP=1151.6
    redshift_fit_1d dja-grism_033239.99-275208.53 F200W dlnP=-0.1



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_18_1.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_18_2.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_18_3.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_18_4.png)
    


### Use original grizli tools to make line maps, measure line fluxes, etc.

Though it still doesn't have a full contamination model....


```python
templ = utils.load_templates(line_complexes=False, fwhm=1500)
splw = np.arange(9000, 3.e4, 5)
bspl = utils.bspline_templates(splw, df=31)
for t in templ:
    if t.startswith('line'):
        bspl[t] = templ[t]

tfit = mb.template_at_z(z=zres['z'], templates=bspl, fitter='lstsq')
_ = mb.drizzle_grisms_and_PAs(tfit=tfit, diff=True, kernel='point',)

if not os.path.exists('fit_args.npy'):
    from grizli.pipeline import auto_script
    fit_args = auto_script.generate_fit_params(include_photometry=False)

```

    Saved arguments to fit_args.npy.



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_20_1.png)
    



```python
# Line map
# mb.drizzle_fit_lines?
# ! ls dja-grism_100014.21+021311.88*

dz = 0.01*(1+zres['z'])

from grizli import fitting, multifit
_ = fitting.run_all_parallel(
    0,
    file_pattern=mb.group_name,
    group_name=mb.group_name,
    get_output_data=True,
    fit_trace_shift=False,
    # zr=(zres['z'], ),                                 # Fix redshift
    zr=zres['z'] + np.array([-1,1])*0.01*(1+zres['z']), # Refit redshift in small range around best fit from above
    verbose=True,
    protect=False,
    # dscale=1./16/8, scale_linemap=4 / 4,
    min_sens=1.e-4, min_cont=1.e-4,
    t0=bspl,
    t1=bspl,
    pline={
        'kernel': 'square',
        'pixfrac': 0.5,
        'pixscale': 0.05,
        'size': 8,
        'wcs': None,
        # aligned with dispersion
        'theta': 270 - mb.beams[0].get_dispersion_PA(decimals=2),
    },
)
```

    Run id=0 with fit_args.npy
    load_master_fits: dja-grism_033239.99-275208.53.beams.fits
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    1 ./jw01283005001_04201_00001_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    2 ./jw01283005001_04201_00002_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    3 ./jw01283005001_04201_00003_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    4 ./jw01283005001_04201_00004_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    5 ./jw01283005001_04201_00005_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    6 ./jw01283005001_04201_00006_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    7 ./jw01283005001_04201_00007_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    8 ./jw01283005001_04201_00008_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    9 ./jw01283005001_04201_00009_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    10 ./jw01283005001_09201_00001_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    11 ./jw01283005001_09201_00002_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    12 ./jw01283005001_09201_00003_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    13 ./jw01283005001_09201_00004_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    14 ./jw01283005001_09201_00005_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    15 ./jw01283005001_09201_00006_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    16 ./jw01283005001_09201_00007_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    17 ./jw01283005001_09201_00008_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    18 ./jw01283005001_09201_00009_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    19 ./jw01283005001_14201_00001_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    20 ./jw01283005001_14201_00002_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    21 ./jw01283005001_14201_00003_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    22 ./jw01283005001_14201_00004_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    23 ./jw01283005001_14201_00005_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    24 ./jw01283005001_14201_00006_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    25 ./jw01283005001_14201_00007_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    26 ./jw01283005001_14201_00008_nis_rate.fits GR150R
    load_new_sensitivity_curve: only defined for NIRCAM (NIRISS)
    27 ./jw01283005001_14201_00009_nis_rate.fits GR150R
    User templates! N=71 
    
    Cache rest-frame template:  bspl 0 9000
    Cache rest-frame template:  bspl 1 9340
    Cache rest-frame template:  bspl 2 9830
    Cache rest-frame template:  bspl 3 10500
    Cache rest-frame template:  bspl 4 11250
    Cache rest-frame template:  bspl 5 12000
    Cache rest-frame template:  bspl 6 12750
    Cache rest-frame template:  bspl 7 13500
    Cache rest-frame template:  bspl 8 14250
    Cache rest-frame template:  bspl 9 15000
    Cache rest-frame template:  bspl 10 15750
    Cache rest-frame template:  bspl 11 16500
    Cache rest-frame template:  bspl 12 17250
    Cache rest-frame template:  bspl 13 18000
    Cache rest-frame template:  bspl 14 18750
    Cache rest-frame template:  bspl 15 19495
    Cache rest-frame template:  bspl 16 20245
    Cache rest-frame template:  bspl 17 20995
    Cache rest-frame template:  bspl 18 21745
    Cache rest-frame template:  bspl 19 22495
    Cache rest-frame template:  bspl 20 23245
    Cache rest-frame template:  bspl 21 23995
    Cache rest-frame template:  bspl 22 24745
    Cache rest-frame template:  bspl 23 25495
    Cache rest-frame template:  bspl 24 26245
    Cache rest-frame template:  bspl 25 26995
    Cache rest-frame template:  bspl 26 27745
    Cache rest-frame template:  bspl 27 28495
    Cache rest-frame template:  bspl 28 29165
    Cache rest-frame template:  bspl 29 29655
    Cache rest-frame template:  bspl 30 29995
    [1A[1M  1.3876   40508.8 (1.3876) 1/6
    [1A[1M  1.3971   38867.2 (1.3971) 2/6
    [1A[1M  1.4067   34276.1 (1.4067) 3/6
    [1A[1M  1.4164   30047.1 (1.4164) 4/6
    [1A[1M  1.4261   35646.2 (1.4164) 5/6
    [1A[1M  1.4358   39717.1 (1.4164) 6/6
    First iteration: z_best=1.4164
    
    zgrid_zoom: 1.4164 [1.4058, 1.4270] N=23
    [1A[1M- 1.4058   34882.7 (1.4058) 1/23
    [1A[1M- 1.4067   34287.2 (1.4067) 2/23
    [1A[1M- 1.4077   33889.2 (1.4077) 3/23
    [1A[1M- 1.4086   33474.8 (1.4086) 4/23
    [1A[1M- 1.4096   33041.9 (1.4096) 5/23
    [1A[1M- 1.4106   32585.3 (1.4106) 6/23
    [1A[1M- 1.4115   31762.5 (1.4115) 7/23
    [1A[1M- 1.4125   30673.6 (1.4125) 8/23
    [1A[1M- 1.4135   30055.3 (1.4135) 9/23
    [1A[1M- 1.4144   29995.7 (1.4144) 10/23
    [1A[1M- 1.4154   30066.1 (1.4144) 11/23
    [1A[1M- 1.4164   30048.4 (1.4144) 12/23
    [1A[1M- 1.4173   30065.4 (1.4144) 13/23
    [1A[1M- 1.4183   30625.2 (1.4144) 14/23
    [1A[1M- 1.4193   31929.9 (1.4144) 15/23
    [1A[1M- 1.4202   33209.7 (1.4144) 16/23
    [1A[1M- 1.4212   33871.7 (1.4144) 17/23
    [1A[1M- 1.4222   34117.9 (1.4144) 18/23
    [1A[1M- 1.4231   34283.6 (1.4144) 19/23
    [1A[1M- 1.4241   34515.7 (1.4144) 20/23
    [1A[1M- 1.4251   34909.4 (1.4144) 21/23
    [1A[1M- 1.4260   35624.6 (1.4144) 22/23
    [1A[1M- 1.4270   36608.0 (1.4144) 23/23
    Cache rest-frame template:  bspl 0 9000
    Cache rest-frame template:  bspl 1 9340
    Cache rest-frame template:  bspl 2 9830
    Cache rest-frame template:  bspl 3 10500
    Cache rest-frame template:  bspl 4 11250
    Cache rest-frame template:  bspl 5 12000
    Cache rest-frame template:  bspl 6 12750
    Cache rest-frame template:  bspl 7 13500
    Cache rest-frame template:  bspl 8 14250
    Cache rest-frame template:  bspl 9 15000
    Cache rest-frame template:  bspl 10 15750
    Cache rest-frame template:  bspl 11 16500
    Cache rest-frame template:  bspl 12 17250
    Cache rest-frame template:  bspl 13 18000
    Cache rest-frame template:  bspl 14 18750
    Cache rest-frame template:  bspl 15 19495
    Cache rest-frame template:  bspl 16 20245
    Cache rest-frame template:  bspl 17 20995
    Cache rest-frame template:  bspl 18 21745
    Cache rest-frame template:  bspl 19 22495
    Cache rest-frame template:  bspl 20 23245
    Cache rest-frame template:  bspl 21 23995
    Cache rest-frame template:  bspl 22 24745
    Cache rest-frame template:  bspl 23 25495
    Cache rest-frame template:  bspl 24 26245
    Cache rest-frame template:  bspl 25 26995
    Cache rest-frame template:  bspl 26 27745
    Cache rest-frame template:  bspl 27 28495
    Cache rest-frame template:  bspl 28 29165
    Cache rest-frame template:  bspl 29 29655
    Cache rest-frame template:  bspl 30 29995
    Drizzle line -> SIII (1.54 0.35)
    Drizzle line -> OII-7325 (0.90 0.35)
    Drizzle line -> ArIII-7138 (8.61 12.55)
    Drizzle line -> SII  (0.63 0.14)
    Drizzle line -> Ha   (10.24 0.13)
    Drizzle line -> OI-6302 (0.63 0.12)
    Drizzle line -> HeI-5877 (0.57 0.10)
    Drizzle line -> OIII (21.49 0.27)
    Drizzle line -> Hb   (3.09 0.14)
    Drizzle line -> OIII-4363 (1.29 0.63)
    Drizzle line -> Hg   (0.09 0.76)
    [1A[1Mdja-grism_033239.99-275208.53_00000.full.fits



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_21_1.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_21_2.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_21_3.png)
    


## NIRCam

Example [OIII] / H$\alpha$ emitters with a PRISM spectrum.




```python
ra, dec, prism_file = 150.1069005, 2.36004609, "cosmos-transients-v4_prism-clear_6585_61234.spec.fits"
ra, dec, prism_file = 150.09900755, 2.34362213, "glazebrook-cos-obs2-v4_prism-clear_2565_15420.spec.fits"
prism_file, ra, dec = 'gto-wide-cos02-v4_prism-clear_1214_727.spec.fits', 150.07850493, 2.35235787

# Show the prism spectrum
prism_mask = prism_file.split("_prism")[0]

Image(f"https://s3.amazonaws.com/msaexp-nirspec/extractions/{prism_mask}/{prism_file.replace('spec.fits', 'fnu.png')}")
```




    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_23_0.png)
    




```python
mb = sky_wfss.extract_from_coords(
    ra=ra,
    dec=dec,
    grisms=['F356W-GRISMR','F430M-GRISMR','F410M-GRISMR','F444W-GRISMR','F444W-GRISMC','F480M-GRISMR','F480M-GRISMC'],
    size=48+32*1,
    grp=None,
    clean=False,
    get_cutout=1,
    cutout_filter=','.join(['F200W-CLEAR','F277W-CLEAR','F356W-CLEAR','F444W-CLEAR'][-3:]), #[::1][-1:]),
    thumbnail_size=0.8 * 2,
    prefix=prefix,
    mb_kwargs={},
    filter_kwargs=[{}, None][1],
    verbose=True,
    local=False,
    use_jwst_crds=False,
    **kwargs
)
```

    https://grizli-cutout.herokuapp.com/exposures?polygon=rect(150.078505,2.352358,0.25)&filters=F356W-GRISMR,F430M-GRISMR,F410M-GRISMR,F444W-GRISMR,F444W-GRISMC,F480M-GRISMR,F480M-GRISMC&output=csv
    extract_from_coords: dja-grism_100018.84+022108.49 10 exposures
    ./jw05893014003_02101_00001_nrcblong_rate.fits exists
    ./jw05893014004_02101_00003_nrcblong_rate.fits exists
    ./jw05893014004_02101_00004_nrcblong_rate.fits exists
    ./jw05893014004_02101_00005_nrcblong_rate.fits exists
    ./jw05893014004_02101_00006_nrcblong_rate.fits exists
    ./jw05893014003_02101_00002_nrcblong_rate.fits exists
    ./jw05893014003_02101_00003_nrcblong_rate.fits exists
    ./jw05893014003_02101_00004_nrcblong_rate.fits exists
    ./jw05893014003_02101_00005_nrcblong_rate.fits exists
    ./jw05893014003_02101_00006_nrcblong_rate.fits exists
    https://grizli-cutout.herokuapp.com/thumb?all_filters=False&filters=f277w-clear,f356w-clear,f444w-clear&ra=150.07850493&dec=2.35235787&size=1.6&output=fits_weight -> dja-grism_100018.84+022108.49_ir.fits
    thumbnail: F277W-CLEAR
    thumbnail: F356W-CLEAR
    thumbnail: F444W-CLEAR
    extract_from_coords: direct image = dja-grism_100018.84+022108.49_ir.fits
     1 / 10 GroupFLT jw05893014003_02101_00001_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     2 / 10 GroupFLT jw05893014004_02101_00003_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     3 / 10 GroupFLT jw05893014004_02101_00004_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     4 / 10 GroupFLT jw05893014004_02101_00005_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     5 / 10 GroupFLT jw05893014004_02101_00006_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     6 / 10 GroupFLT jw05893014003_02101_00002_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     7 / 10 GroupFLT jw05893014003_02101_00003_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     8 / 10 GroupFLT jw05893014003_02101_00004_nrcblong_rate.fits
    Using default C-based coordinate transformation...
     9 / 10 GroupFLT jw05893014003_02101_00005_nrcblong_rate.fits
    Using default C-based coordinate transformation...
    10 / 10 GroupFLT jw05893014003_02101_00006_nrcblong_rate.fits
    Using default C-based coordinate transformation...
    extract_from_coords: dja-grism_100018.84+022108.49 6 beam cutouts



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_24_1.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_24_2.png)
    


Contamination or background over-subtraction can look troublesome, but can still find the line using the flexible contamination / continuum model


```python
# Just show the simplified 1D extraction

from importlib import reload
reload(sky_wfss)

dv = 50 * 3

b2d, zres = sky_wfss.combine_beams_2d(
    mb,
    step=0.5, pixfrac=0.75,
    ymax=12.5,
    profile_sigma=1.5, profile_offset=-0.5, profile_type="gaussian",     # Gaussian cross-dispersion model
    # profile_type="grizli",                                   # Use the direct image thumbnail
    bkg_percentile=None,
    cont_spline=31*1, zfit_nspline=-1,
    zfit_kwargs=None,
)

```

    final spectrum file: dja-grism_100018.84+022108.49.f444w.spec.fits



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_26_1.png)
    



```python
# Do the redshift fit

dv = 150 # km/s

b2d, zres = sky_wfss.combine_beams_2d(
    mb,
    step=0.5, pixfrac=0.75,
    ymax=12.5,
    profile_sigma=1.5, profile_offset=-0.5, profile_type="gaussian",     # Gaussian cross-dispersion model
    # profile_type="grizli",                                   # Use the direct image thumbnail
    bkg_percentile=None,
    cont_spline=31*1, zfit_nspline=-1,
    # cont_spline=0, zfit_nspline=31,
    zfit_kwargs=dict(
        rest_wave=[6800, 4800], # Halpha - OIII
        velocity_sigma=dv,
        dz=dv/3.e5/2,
    ),
)
```

    final spectrum file: dja-grism_100018.84+022108.49.f444w.spec.fits
    redshift_fit_1d dja-grism_100018.84+022108.49 z=[4.618, 9.582] dz=0.00025  nsteps=2534
    redshift_fit_1d dja-grism_100018.84+022108.49 best z=5.25520  dlnP=113.8
    redshift_fit_1d dja-grism_100018.84+022108.49 F444W dlnP=113.8



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_27_1.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_27_2.png)
    


### Compare to PRISM spectrum


```python
# Prism spectrum
import msaexp.spectrum
prism = msaexp.spectrum.SpectrumSampler(
    f"https://s3.amazonaws.com/msaexp-nirspec/extractions/{prism_mask}/{prism_file}"
)
```


```python

fig, axes = plt.subplots(1,2,figsize=(10, 4), sharey=True)
for ax in axes:
    ax.plot(prism['wave'], prism['flux'] * prism['to_flam'], label=prism_file, color='k', alpha=0.5)

    for gr in b2d:
        grism = b2d[gr]['spec']
        for PA in mb.PA[gr]:
            ix = mb.PA[gr][PA][0]
            break

        sens = np.interp(grism['wave']*1.e4, mb.beams[ix].beam.lam, mb.beams[ix].beam.sensitivity)
        trim = sens > 0.05*sens.max()
        ax.plot(grism['wave'][trim], (grism['flux'] / sens)[trim] * 1.e20, label=gr, alpha=0.5)

    ax.set_ylim(-5, 25)
    ax.grid()

for lrest in [5008, 6564.]:
    lobs = lrest * (1 + zres['z']) / 1.e4
    if lobs > grism['wave'].min():
        ax.set_xlim(lobs - 0.1, lobs + 0.1)
        break

axes[0].set_ylabel(r'$f_\lambda$ [$10^{-20}$ erg$~$/$~$s$~$/$~$cm$^2~$/$~\mathrm{\AA}$]')
# ax.set_xlim(3.8, 4.2)
# ax.set_xlim(4.5, 5.0)
fig.tight_layout(pad=1)
```


    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_30_0.png)
    


### Line map


```python
templ = utils.load_templates(line_complexes=False, fwhm=150)
splw = np.arange(9000, 3.e4, 5)
bspl = utils.bspline_templates(splw, df=31)
for t in templ:
    if t.startswith('line'):
        bspl[t] = templ[t]

tfit = mb.template_at_z(z=zres['z'], templates=bspl, fitter='lstsq')
_ = mb.drizzle_grisms_and_PAs(tfit=tfit, diff=True, kernel='point',)

if not os.path.exists('fit_args.npy'):
    from grizli.pipeline import auto_script
    fit_args = auto_script.generate_fit_params(include_photometry=False)

```


    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_32_0.png)
    



```python
# Line map
# mb.drizzle_fit_lines?
# ! ls dja-grism_100014.21+021311.88*

fit_res = fitting.run_all_parallel(
    0,
    file_pattern=mb.group_name,
    group_name=mb.group_name,
    get_output_data=True,
    fit_trace_shift=False,
    zr=(zres['z'], ),                                 # Fix redshift
    # zr=zres['z'] + np.array([-1,1])*0.001*(1+zres['z']), # Refit redshift in small range around best fit from above
    verbose=True,
    protect=False,
    # dscale=1./16/8, scale_linemap=4 / 4,
    min_sens=1.e-4, min_cont=1.e-4,
    t0=bspl,
    t1=bspl,
    pline={
        'kernel': 'square',
        'pixfrac': 0.5,
        'pixscale': 0.05,
        'size': 8,
        'wcs': None,
        # aligned with dispersion
        'theta': 270 - mb.beams[0].get_dispersion_PA(decimals=2),
    },
)
```

    Run id=0 with fit_args.npy
    load_master_fits: dja-grism_100018.84+022108.49.beams.fits
    1 ./jw05893014003_02101_00001_nrcblong_rate.fits F444W
    2 ./jw05893014003_02101_00002_nrcblong_rate.fits F444W
    3 ./jw05893014003_02101_00003_nrcblong_rate.fits F444W
    4 ./jw05893014003_02101_00004_nrcblong_rate.fits F444W
    5 ./jw05893014003_02101_00005_nrcblong_rate.fits F444W
    6 ./jw05893014003_02101_00006_nrcblong_rate.fits F444W
    User templates! N=71 
    
    Cache rest-frame template:  bspl 0 9000
    Cache rest-frame template:  bspl 1 9340
    Cache rest-frame template:  bspl 2 9830
    Cache rest-frame template:  bspl 3 10500
    Cache rest-frame template:  bspl 4 11250
    Cache rest-frame template:  bspl 5 12000
    Cache rest-frame template:  bspl 6 12750
    Cache rest-frame template:  bspl 7 13500
    Cache rest-frame template:  bspl 8 14250
    Cache rest-frame template:  bspl 9 15000
    Cache rest-frame template:  bspl 10 15750
    Cache rest-frame template:  bspl 11 16500
    Cache rest-frame template:  bspl 12 17250
    Cache rest-frame template:  bspl 13 18000
    Cache rest-frame template:  bspl 14 18750
    Cache rest-frame template:  bspl 15 19495
    Cache rest-frame template:  bspl 16 20245
    Cache rest-frame template:  bspl 17 20995
    Cache rest-frame template:  bspl 18 21745
    Cache rest-frame template:  bspl 19 22495
    Cache rest-frame template:  bspl 20 23245
    Cache rest-frame template:  bspl 21 23995
    Cache rest-frame template:  bspl 22 24745
    Cache rest-frame template:  bspl 23 25495
    Cache rest-frame template:  bspl 24 26245
    Cache rest-frame template:  bspl 25 26995
    Cache rest-frame template:  bspl 26 27745
    Cache rest-frame template:  bspl 27 28495
    Cache rest-frame template:  bspl 28 29165
    Cache rest-frame template:  bspl 29 29655
    Cache rest-frame template:  bspl 30 29995
    [1A[1M  5.2552  196564.9 (5.2552) 1/1
    First iteration: z_best=5.2552
    
    Cache rest-frame template:  bspl 0 9000
    Cache rest-frame template:  bspl 1 9340
    Cache rest-frame template:  bspl 2 9830
    Cache rest-frame template:  bspl 3 10500
    Cache rest-frame template:  bspl 4 11250
    Cache rest-frame template:  bspl 5 12000
    Cache rest-frame template:  bspl 6 12750
    Cache rest-frame template:  bspl 7 13500
    Cache rest-frame template:  bspl 8 14250
    Cache rest-frame template:  bspl 9 15000
    Cache rest-frame template:  bspl 10 15750
    Cache rest-frame template:  bspl 11 16500
    Cache rest-frame template:  bspl 12 17250
    Cache rest-frame template:  bspl 13 18000
    Cache rest-frame template:  bspl 14 18750
    Cache rest-frame template:  bspl 15 19495
    Cache rest-frame template:  bspl 16 20245
    Cache rest-frame template:  bspl 17 20995
    Cache rest-frame template:  bspl 18 21745
    Cache rest-frame template:  bspl 19 22495
    Cache rest-frame template:  bspl 20 23245
    Cache rest-frame template:  bspl 21 23995
    Cache rest-frame template:  bspl 22 24745
    Cache rest-frame template:  bspl 23 25495
    Cache rest-frame template:  bspl 24 26245
    Cache rest-frame template:  bspl 25 26995
    Cache rest-frame template:  bspl 26 27745
    Cache rest-frame template:  bspl 27 28495
    Cache rest-frame template:  bspl 28 29165
    Cache rest-frame template:  bspl 29 29655
    Cache rest-frame template:  bspl 30 29995


    WARNING:py.warnings:/usr/local/lib/python3.11/dist-packages/grizli/fitting.py:4217: UserWarning: Attempting to set identical low and high xlims makes transformation singular; automatically expanding.
      axz.set_xlim(zmi, zma)
    
    2025-05-16 20:52:17,962 - stpipe - WARNING - /usr/local/lib/python3.11/dist-packages/grizli/fitting.py:4217: UserWarning: Attempting to set identical low and high xlims makes transformation singular; automatically expanding.
      axz.set_xlim(zmi, zma)
    
    WARNING:stpipe:/usr/local/lib/python3.11/dist-packages/grizli/fitting.py:4217: UserWarning: Attempting to set identical low and high xlims makes transformation singular; automatically expanding.
      axz.set_xlim(zmi, zma)
    
    WARNING:py.warnings:/usr/local/lib/python3.11/dist-packages/grizli/fitting.py:944: UserWarning: Attempting to set identical low and high xlims makes transformation singular; automatically expanding.
      axz.set_xlim(zmi, zma)
    
    2025-05-16 20:52:19,515 - stpipe - WARNING - /usr/local/lib/python3.11/dist-packages/grizli/fitting.py:944: UserWarning: Attempting to set identical low and high xlims makes transformation singular; automatically expanding.
      axz.set_xlim(zmi, zma)
    
    WARNING:stpipe:/usr/local/lib/python3.11/dist-packages/grizli/fitting.py:944: UserWarning: Attempting to set identical low and high xlims makes transformation singular; automatically expanding.
      axz.set_xlim(zmi, zma)
    


    Drizzle line -> OII-7325 (-0.85 0.23)
    Drizzle line -> ArIII-7138 (-0.41 0.18)
    Drizzle line -> SII  (0.01 0.22)
    Drizzle line -> Ha   (2.97 0.16)
    Drizzle line -> OI-6302 (-1.05 0.19)
    [1A[1Mdja-grism_100018.84+022108.49_00000.full.fits



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_33_3.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_33_4.png)
    



    
![png]({{ site.baseurl }}/assets/post_files/2025-05-16-simplified_cutout_wfss_files/simplified_cutout_wfss_33_5.png)
    

