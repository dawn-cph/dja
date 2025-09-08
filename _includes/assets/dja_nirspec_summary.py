import numpy as np

from grizli.aws import db
from grizli import utils

version = "v4"

nre = db.SQL("""select file, root, grating || '-' || filter as grating, msamet, effexptm, exptime from nirspec_extractions
where root like '%%v3'
AND root not like 'rubies%%-nod-v3' AND root not like 'rubies%%-xoff-v3'
AND root not like 'jw0%%'
AND root not like 'mom-cos%%'
AND root not like 'uncover-flash%%'
""".replace("v3", version))

nre['prog'] = [m[3:7] for m in nre['msamet']]

nrm = db.SQL("""select objid, file, ra, dec, z
from nirspec_unique natural join nirspec_unique_match
where file like '%%-v3%%'
""".replace("v3", version))

nrmz = nrm[nrm['z'] > -0.1]

utils.Unique(nre['prog'], verbose=False)

un = utils.Unique(nre['prog'], verbose=False)

labels = utils.read_catalog("dja_nirspec_references.csv")

from tqdm import tqdm

rows = []

lines = ["""
|  JWST program |  Survey       |   ``root``    | Grating-Filter (t) | *N* total  | *N* ``grade=3``  |
|:-------------:|:-------------:|--------------:|-------------------:|-----------:|-----------------:|"""]
print(lines[0])

rowstr = '| [{0}](https://www.stsci.edu/jwst-program-info/program/?program={0}) |  {5} |  {1} | {2} | {3} | {4} |'

for v in un.values:
    if v in ['x1208', 'x4318', 'x1635', '1226', 'x3567', 'x1835','4713','4527','4598']:
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
    
    if survey == '':
        print(f"Missing: {int(v)}")
    
    root_links = [
    # f'[{root}](https://s3.amazonaws.com/msaexp-nirspec/extractions/{root}/index.html)'
    f'[{root}](https://s3.amazonaws.com/msaexp-nirspec/extractions/nirspec_public_v4.4.html?&search={root})'
    for root in roots
    ]
    row = [
        v,
        ' <br> '.join(root_links), ' <br> '.join(grating_summary), n_un, n_unz, survey]
    
    line = rowstr.format(*row)
    lines.append(line)

    # break

with open(f'dja_nirspec_summary_{version}.md','w') as fp:
    for line in lines:
        fp.write(line + '\n')