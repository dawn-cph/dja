import numpy as np

from grizli.aws import db
from grizli import utils

nre = db.SQL("""select file, root, grating || '-' || filter as grating, msamet, effexptm, exptime from nirspec_extractions
where root like '%%v3'
AND root not like 'rubies%%-nod-v3' AND root not like 'rubies%%-xoff-v3'""")

nre['prog'] = [m[3:7] for m in nre['msamet']]

nrm = db.SQL("""select objid, file, ra, dec, z
from nirspec_unique natural join nirspec_unique_match
where file like '%%-v3%%'
""")
nrmz = nrm[nrm['z'] > -0.1]

utils.Unique(nre['prog'], verbose=False)

un = utils.Unique(nre['prog'])

labels = utils.read_catalog("""prog, survey
1180, JADES <br> [D'Eugenio et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240406531D)
1181, JADES
1199, GTO [Stiavelli et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...957L..18S)
1207, GTO (G. Rieke)
1208, CANUCS <br> [Willott et al. (2022)](https://ui.adsabs.harvard.edu/abs/2022PASP..134b5002W)
1210, JADES
1211, GTO WIDE <br> [Maseda et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024A%26A...689A..73M)
1212, GTO WIDE
1213, GTO WIDE
1214, GTO WIDE
1215, GTO WIDE
1286, JADES
1287, JADES
1324, GLASS-ERS <br> [Mascia et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024A%26A...690A...2M/abstract)
1345, CEERS-ERS <br> [Finkelstein et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...946L..13F)
1433, MACS-J0647 <br> [Hsiao et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...973....8H) 
1747, BoRG (G. Roberts-Borsani)
1810, Bluejay <br> [Belli et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024Natur.630...54B)
1869, LyC-22 <br> (D. Schaerer)
1871, (J. Chisholm)
1879, (M. Curti)
1914, AURORA <br> [Shapely et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240700157S)
2028, [Wang et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...962L..11W)
2073, (J. Hennawi)
2110, SUSPENSE <br> [Slob et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...973..131S)
2198, [Barrufet et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240408052B)
2282, [Bradley et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...955...13B)
2478, (D. Stark)
2561, UNCOVER <br> [Bezanson et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...974...92B)
2565, [Nanayakkara et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv241002076N)
2593, CECILIA <br> [Strom et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJ...958L..11S)
2674, (P. Arrabal Haro)
2750, [Arrabal Haro et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023Natur.622..707A)
2756, (W. Chen)
2736, SMACS-0723 ERO <br> [Pontoppidan et al. (2022)](https://ui.adsabs.harvard.edu/abs/2022ApJ...936L..14P)
2767, [Williams et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023Sci...380..416W)
3073, [Castellano et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024ApJ...972..143C)
3567, (F. Valentino)
3215, JADES Ultra-Deep <br> [Eisenstein et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023arXiv231012340E)
3543, EXCELS <br> [Carnall et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024MNRAS.534..325C)
4106, (E. Nelson)
4233, RUBIES <br> [de Graaff et al. (2024)](https://ui.adsabs.harvard.edu/abs/2024arXiv240905948D/abstract)
4246, (A. Abdurro'uf)
4318, (J. Antwi-Danso)
4446, [Frye et al. (2023)](https://ui.adsabs.harvard.edu/abs/arXiv:2309.07326)
4557, (H. Yan)
5224, (R. Naidu &amp; P. Oesch)
6368, CAPERS (M. Dickinson)
6541, (E. Egami)
6585, (D. Coulter)
""", format="csv")

from tqdm import tqdm

rows = []

lines = ["""
|  JWST program |  Survey       |   ``root``    | Grating-Filter (t) | *N* total  | *N* ``grade=3``  |
|:-------------:|:-------------:|--------------:|-------------------:|-----------:|-----------------:|"""]
print(lines[0])

rowstr = '| [{0}](https://www.stsci.edu/jwst-program-info/program/?program={0}) |  {5} |  {1} | {2} | {3} | {4} |'

for v in un.values:
    if v in ['1208', '4318', '1635', '1226', '3567', '1835', '5224', '6368']:
        continue
        
    uv = un[v]
    roots = np.unique(nre['root'][uv])
    in_un = np.isin(nrm['file'], nre['file'][uv])
    n_un = len(np.unique(nrm['objid'][in_un]))
    in_unz = np.isin(nrmz['file'], nre['file'][uv])
    n_unz = len(np.unique(nrmz['objid'][in_unz]))

    gra = utils.Unique(nre['grating'][uv], verbose=False)
    grating_summary = []
    for gr in gra.values:
        expt = np.median(nre['exptime'][uv][gra[gr]]) / 3600.
        grating_summary.append(f'{gr} ({expt:4.1f})')

    survey = labels['survey'][labels['prog'] == int(v)][0] if int(v) in labels['prog'] else ''
    row = [v, ' <br> '.join(roots.tolist()), ' <br> '.join(grating_summary), n_un, n_unz, survey]
    
    line = rowstr.format(*row)
    lines.append(line)

    # break

with open('dja_nirspec_summary.md','w') as fp:
    for line in lines:
        fp.write(line + '\n')