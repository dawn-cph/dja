---
layout: page
title: Data Dashboard
showGeneral: true
navigation_weight: 14
---

Summary of recent and upcoming **public** datasets.

MAST queries performed with [generate_data_dashboard.py]( {{ site.baseurl }}{% link assets/dashboard/generate_data_dashboard.py %}), which is roughly tuned for "extra-solar" datasets excluding subarray observations and ``Solar System Astronomy`` and ``Exoplanets and Exoplanet Formation`` proposal categories. 

Skip down to [Imaging](#imaging), [NIRSpec](#nirspec-spectroscopy), [MIRI Spectroscopy](#miri-spectroscopy).

### Imaging

```python
subarray = "FULL"
exp_type = ["MIR_IMAGE", "NIS_IMAGE", "NIS_WFSS", "NRC_WFSS"]
```

{% include assets/dashboard/imaging.md %}

### NIRSpec Spectroscopy

```python
exp_type = ["NRS_IFU", "NRS_FIXEDSLIT", "NRS_MSASPEC"]
````

{% include assets/dashboard/nirspec.md %}

### MIRI Spectroscopy

```python
exp_type = ["MIR_LRS-FIXEDSLIT", "MIR_MRS"]
````

{% include assets/dashboard/mirispec.md %}
