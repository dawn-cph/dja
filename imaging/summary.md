---
layout: page
title: NIRCam + NIRISS imaging
showImageDataset: true
navigation_weight: 10
---

<div class="image fit caption">
    <img src="{{site.baseurl}}/images/fields.jpg" alt="v6 fields">

    Many JWST survey fields

</div>

Here you will find various ways to access the imaging data:

- [v7]({{site.baseurl}}/imaging/v7/): Latest release of JWST mosaics (July 2023)
- [v6]({{site.baseurl}}/imaging/v6/): Previous release, including some HST mosaics that were not regenerated for v7.
- The [image-data-products]({{ site.baseurl }}/blog/2023/07/18/image-data-products/) post describes the image mosaics
- The [photometric-catalog-demo]({{ site.baseurl }}/blog/2023/07/14/photometric-catalog-demo/) post describes the aperture photometry catalogs derived automatically from the mosaics
- For pannable images with various possible layers, including HST and JWST filters as well as spectral observations, see the [Map View]({{ site.baseurl }}/general/mapview/) pages. To see individual spectra, pan over a source with the different *Spectra* overlays enabled.

> More documentation is coming soon, but for now, the image reduction process is
> described in [Valentino et
> al., 2023](https://ui.adsabs.harvard.edu/abs/2023ApJ...947...20V/abstract) and 
> the [grizli](https://github.com/gbrammer/grizli) software is freely available.


## Citing imaging programs

The script below can be used to generate a list of HST and JWST programs that
contribute to a particular DJA image mosaic.

```python
from grizli import utils
import numpy as np

# Read summary tables
hst = utils.read_catalog('https://dawn-cph.github.io/dja/data/hst_program_codes.csv')
hst_programs = {}
hst_pi = {}
for row in hst:
    hst_programs[row['prog_code']] = row['proposal_id']
    hst_pi[str(row['proposal_id'])] = row['pi']

jw = utils.read_catalog('https://dawn-cph.github.io/dja/data/jwst_program_codes.csv')
jwst_pi = {}
for row in jw:
    jwst_pi[str(row['proposal_id'])] = row['pi']

# grizli WCS summary file, remote or local
wcs_file = 'https://s3.amazonaws.com/grizli-v2/JwstMosaics/v7/gds-grizli-v7.0-f850lp_wcs.csv'
exp = utils.read_catalog(wcs_file)

# Loop through file names and calculate program IDs
progs = []
for file in np.unique(exp['file']):
    if file.startswith('jw'):
        progs.append(f'JWST-{file[3:7]}')
    else:
        progs.append(f'HST-{hst_programs[file[1:4]]}')
        
# Print a summary
un = utils.Unique(progs, verbose=False)

print('# ' + os.path.basename(wcs_file))
print('|    N  |  ProgID     | PI                    | Info |')
print('|------:|:-----------:|-----------------------|------|')
for v in un.values:
    obs, prog = v.split('-')
    pi = hst_pi[prog] if obs == 'HST' else jwst_pi[prog]
    url = f'https://www.stsci.edu/cgi-bin/get-proposal-info?id={prog}&observatory={obs}'
    
    print(f"| {un[v].sum():>4}  |  {v:>9}  |  {pi.split(',')[0]:>20} | [{url}]({url}) | ")
```

Prints: 

`# gds-grizli-v7.0-f850lp_wcs.csv`

|    N  |  ProgID     | PI                    | Info |
|------:|:-----------:|-----------------------|------|
|   16  |  HST-10086  |              Beckwith | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=10086&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=10086&observatory=HST) | 
|   46  |  HST-10189  |                 Riess | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=10189&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=10189&observatory=HST) | 
|   36  |  HST-10258  |             Kretchmer | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=10258&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=10258&observatory=HST) | 
|  272  |  HST-10340  |                 Riess | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=10340&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=10340&observatory=HST) | 
|   16  |  HST-10632  |             Stiavelli | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=10632&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=10632&observatory=HST) | 
|  144  |  HST-11563  |           Illingworth | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=11563&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=11563&observatory=HST) | 
|   56  |  HST-12060  |                 Faber | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=12060&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=12060&observatory=HST) | 
|   15  |  HST-12061  |                 Faber | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=12061&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=12061&observatory=HST) | 
|   25  |  HST-12062  |                 Faber | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=12062&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=12062&observatory=HST) | 
|   16  |  HST-12099  |                 Riess | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=12099&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=12099&observatory=HST) | 
|    8  |  HST-12461  |                 Riess | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=12461&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=12461&observatory=HST) | 
|    4  |  HST-12534  |               Teplitz | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=12534&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=12534&observatory=HST) | 
|   40  |   HST-9352  |                 Riess | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=9352&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=9352&observatory=HST) | 
|  228  |   HST-9425  |            Giavalisco | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=9425&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=9425&observatory=HST) | 
|    5  |   HST-9488  |            Ratnatunga | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=9488&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=9488&observatory=HST) | 
|   15  |   HST-9500  |                   Rix | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=9500&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=9500&observatory=HST) | 
|   10  |   HST-9803  |              Thompson | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=9803&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=9803&observatory=HST) | 
|  272  |   HST-9978  |              Beckwith | [https://www.stsci.edu/cgi-bin/get-proposal-info?id=9978&observatory=HST](https://www.stsci.edu/cgi-bin/get-proposal-info?id=9978&observatory=HST) | 