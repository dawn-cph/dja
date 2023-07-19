---
layout: page
title: jwst-sources Repository
showGeneralDataset: true
navigation_weight: 12
---

At [https://github.com/dawn-cph/jwst-sources](https://github.com/dawn-cph/jwst-sources) we have started collating a list of individual JWST sources described in the literature to facilitate more efficient cross-matching and citation of relevant works.

For example, say you're looking through the [CEERS mosaic](https://s3.amazonaws.com/grizli-v2/ClusterTiles/Map/egs-v2/index.html?coord=214.9145541,52.9430222&zoom=6) and find a source at ``(RA, Dec.) = (214.91455, 52.943023)`` that [looks like](https://grizli-cutout.herokuapp.com/thumb?all_filters=True&size=3&scl=1&asinh=False&filters=f150w-clear,f200w-clear,f277w-clear&rgb_scl=1.1,1.3,1.5&pl=2.0&ra=214.9145541&dec=52.9430222) it could be at z = 16.  Has anybody else seen (and published) that source before?

```python
>>> import numpy as np

>>> from astropy.table import Table

>>> url = 'https://jwst-sources.herokuapp.com/match?coords={0}%20{1}&sep=2&output=csv'

>>> ra, dec = 214.91455, 52.943023

>>> jw = Table.read(url.format(ra, dec), format='csv')

>>> so = np.argsort(jw['arxiv'])

>>> jw['arxiv','author','ra','dec','dr','zphot','zspec'][so].to_pandas()
        arxiv              author         ra       dec    dr  zphot  zspec
0  2207.12356       Callum Donnan  214.91450  52.94303  0.11  16.74    NaN
1  2208.02794         Rohan Naidu  214.91450  52.94304  0.12   5.00    NaN
2  2303.15431  Pablo Arrabal Haro  214.91455  52.94302  0.01  16.45  4.912
```

*Yes!*

The repository is currently an incomplete list of all of the exciting sources that have already been discovered in the first year of JWST observations.  Please add your own reference(s) via a Pull Request on the [jwst-sources](https://github.com/dawn-cph/jwst-sources#adding-new-references) repository today!