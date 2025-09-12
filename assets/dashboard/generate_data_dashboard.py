import numpy as np
import os
import time

import mastquery
import mastquery.jwst
from grizli.aws import db
from grizli import utils

import astropy.time

now = utils.nowtime().mjd
now_iso = utils.nowtime().iso
print(now_iso)

dt = 30

def query_summary(res):
    # uni = utils.Unique(res['program'], verbose=False)

    if hasattr(res["scicat"], "mask"):
        res["scicat"] = res["scicat"].filled("")
    
    res["scicat"][np.isin(res["scicat"], [None])] = ""

    uni = utils.Unique(
        ["{program}-{targprop}".format(**r) for r in res["program", "targprop"]],
        verbose=False,
    )  # res['program'], verbose=False)

    # count	proposal_id	pi_name	scicat	targprop	gfilt	min_wait	max_wait
    rows = []

    for p in uni.values:
        pi = uni[p]
        i = np.where(pi)[0][0]
        row_i = res[i]

        so = np.argsort(res["release"][pi])

        row = {
            "count": f'{pi.sum()}',
            "proposal_id": "[{category}-{program}](https://www.stsci.edu/jwst-program-info/visits/?program={program})".format(
                **row_i
            ),
            "pi_name": row_i["pi_name"].split(",")[0],
            "category": row_i["scicat"],
            "targprop": " ".join(np.unique(res["targprop"][pi]).tolist()),
            "exp_type": " ".join(np.unique(res["exp_type"][pi]).tolist())
            .replace("NRS_", "")
            .replace("FIXEDSLIT", "FS")
            .replace("LRS-FS", "LRS")
            .replace("MSASPEC", "MSA"),
            "observed": res["observed"][pi][so[0]][: len("2025-09-01 01:18")],
            "release": res["release"][pi][so[0]][: len("2025-09-01 01:18")],
            # "last": res['release'][pi][so[-1]][:len("2025-09-01 01:18")],
        }

        cats = {
            "Stellar Populations and the Interstellar Medium": "Stellar Pops + ISM",
            "High-redshift Galaxies and the Distant Universe": "High-z Galaxies",
            "Large Scale Structure of the Universe": "LSS",
            "Stellar Physics and Stellar Types": "Stellar Phyisics",
            "Supermassive Black Holes and Active Galaxies": "SMBH + Active Galaxies",
        }

        for k in cats:
            row["category"] = row["category"].replace(k, cats[k])

        if "grating" in res.colnames:
            gfilt = ["{grating}-{filter}".format(**r) for r in res[pi]]
            row["bandpass"] = " ".join(np.unique(gfilt).tolist())
        elif "filter-pupil" in res.colnames:
            bp = " ".join(np.unique(res["filter-pupil"][pi]).tolist())
            bp = (
                bp.replace("F444W-CLEAR", "F444W")
                .replace("F150W2-CLEAR", "F150W2")
                .replace("CLEARP", "CLEAR")
                .replace("-CLEAR", "")
            )
            bp = bp.replace("CLEAR-", "")
            row["bandpass"] = " ".join(np.unique(bp.split()).tolist())

            # row["mode"]
        elif "pupil" in res.colnames:
            gfilt = ["{filter}-{pupil}".format(**r) for r in res[pi]]
            row["bandpass"] = " ".join(np.unique(gfilt).tolist())

        if "targ_ra" in res.colnames:
            ra = np.mean(res["targ_ra"][pi])
            dec = np.mean(res["targ_dec"][pi])

            row["coords"] = (
                f"[{utils.radec_to_targname(ra, dec)}](https://www.legacysurvey.org/viewer?ra={ra:.5f}&dec={dec:.5f}&layer=ls-dr10&zoom=13)"
            )

        targets = np.unique(res["targprop"][pi])

        rows.append(row)

    summ = utils.GTable(rows)
    so = np.argsort(summ["release"])

    cols = [
        "count",
        "proposal_id",
        "pi_name",
        "category",
        "targprop",
        "coords",
        "exp_type",
        "bandpass",
        "observed",
        "release",
    ]

    summ = summ[cols][so]
    pub_split = summ['release'] > now_iso
    if pub_split.sum() > 0:
        j = np.where(pub_split)[0][0]
        summ.insert_row(
            j,
            vals={
                "count":"",
                "observed": "**Query**",
                "release": "**" + now_iso[:len("2025-09-01 01:18")] + "**"
            }
        )
        
    return summ


def dashboard_nirspec():
    ### NIRSpec
    progs = [1180]
    extra_filters = []


    extra_filters = []

    progs = None

    # extra_filters += mastquery.jwst.make_query_filter('apername', values=['NRS_FULL_MSA','NRS_FULL_IFU']])
    # extra_filters += mastquery.jwst.make_query_filter('category', values=['GTO','GO','DD','ERS','CAL','COM'])
    extra_filters += mastquery.jwst.make_query_filter(
        "exp_type", values=["NRS_IFU", "NRS_FIXEDSLIT", "NRS_MSASPEC"]
    )
    # extra_filters += mastquery.jwst.make_query_filter('subarray', values=['FULL','NRS_FIXEDSLIT'])

    # extra_filters += mastquery.jwst.make_query_filter("is_imprt", values=["f",None]) # Not Imprint

    # Public
    extra_filters += mastquery.jwst.make_query_filter(
        "publicReleaseDate_mjd", range=[now - dt, now + dt]
    )

    GRATINGS = ["prism", "g140m", "g140h", "g235m", "g235h", "g395m", "g395h"]
    FILTERS = ["clear", "f070lp", "f100lp", "f170lp", "f290lp"]
    ACQ_FILTERS = ["f140x", "f110w"]
    DETECTORS = ["nrs1", "nrs2"]

    extra_filters += mastquery.jwst.make_query_filter("detector", values=["nrs1"])
    extra_filters += mastquery.jwst.make_query_filter("grating", values=GRATINGS)

    extensions = ["rate", "uncal", "cal"]  #'s2d','s3d']
    # extensions = ['cal']

    product = "rate"

    # progs = [3722]
    query = []

    progs = []

    extra_filters += mastquery.jwst.make_query_filter(
        "productLevel",
        values=["1", "1a", "1b", "2", "2a", "2b"],
    )

    if progs is not None:
        query += mastquery.jwst.make_program_filter(progs)

    print("Query: ")
    for q in query + extra_filters:
        print(q)

    res = mastquery.jwst.query_jwst(
        instrument="NRS",
        filters=query + extra_filters,
        extensions=extensions,
        # recent_days=2000,
        rates_and_cals=False,
    )


    # Unique rows
    rates = []
    unique_indices = []

    if 0:
        for i, u in enumerate(res["dataURI"]):
            ui = u.replace("s2d", product)
            for e in extensions:
                ui = ui.replace(e, product)

            if ui not in rates:
                unique_indices.append(i)

            rates.append(ui)

        res.remove_column("dataURI")
        res["dataURI"] = rates

        res = res[unique_indices]

    skip = np.isin(res["filter"], ["OPAQUE"])
    skip |= np.isin(
        res["scicat"], ["Solar System Astronomy", "Exoplanets and Exoplanet Formation"]
    )

    if "is_imprt" in res.colnames:
        for j, imp in enumerate(res["is_imprt"]):
            skip[j] |= imp == "t"

    if skip.sum() > 0:
        print(f"Remove {skip.sum()} rows with filter=OPAQUE or is_imprt")
        res = res[~skip]

    res["release"] = astropy.time.Time(res["publicReleaseDate_mjd"], format="mjd").iso

    res["observed"] = astropy.time.Time(res["expstart"], format="mjd").iso

    so = np.argsort(res["publicReleaseDate_mjd"])
    res = utils.GTable(res[so])

    for i, file in enumerate(res["filename"]):
        file = file.replace("_cal", "_rate").replace("_uncal", "_rate")
        res["filename"][i] = file

    un = utils.Unique(res["filename"], verbose=False)
    res = res[un.unique_index(0)]

    so = np.argsort(res["date_beg_mjd"])
    res = utils.GTable(res[so])
    
    print(f"NIRSpec: {len(res)} rows")
    
    res.write("../../../assets/dashboard/nirspec.csv", overwrite=True)

    if len(res) > 0:
        with open("nirspec.md","w") as fp:
            fp.write(f"""
xxx query: *{now_iso[:len("2025-09-01 01:18")]} ± {dt} days*

""".replace("xxx","[nirspec.csv]( {{ site.baseurl }}{% link assets/dashboard/nirspec.csv %} )"))
            fp.write(query_summary(res).to_pandas().to_markdown(index=False))


def dashboard_imaging():
    now = astropy.time.Time.now().mjd
    instruments = ["MIR", "NRC", "NIS"]  # ,'NRS']

    filters = []

    filters += mastquery.jwst.make_query_filter(
        "publicReleaseDate_mjd", range=[now - dt, now + dt]
    )
    filters += mastquery.jwst.make_query_filter(
        "productLevel", values=["1a", "1b", "2a", "2b"]
    )

    filters += mastquery.jwst.make_query_filter("subarray", values=["FULL"])

    filters += mastquery.jwst.make_query_filter(
        "detector", values=["MIRIMAGE", "NIS", "NRCA1", "NRCALONG", "NRCB1", "NRCBLONG"]
    )
    filters += mastquery.jwst.make_query_filter(
        "exp_type", values=["MIR_IMAGE", "NIS_IMAGE", "NRC_IMAGE", "NIS_WFSS", "NRC_WFSS"]
    )

    filters += mastquery.jwst.make_query_filter("patt_num", values=[1])

    extensions = ["rate", "cal", "rateints", "uncal"]

    res = mastquery.jwst.query_all_jwst(
        instruments=instruments,
        # recent_days=days,
        filters=filters,
        columns="*",
        extensions=extensions,
        fix=True,
    )  # (not IS_PASSAGE))

    res["release"] = astropy.time.Time(res["publicReleaseDate_mjd"], format="mjd").iso
    res["observed"] = astropy.time.Time(res["expstart"], format="mjd").iso

    res = res[np.isin(res["instrument_name"], ["NIRISS", "NIRCAM", "MIRI"])]

    # No MIRI spec
    res = res[res["inst-mode"] != "MIRI-None"]
    res = res[res["targname"] != "MIRI-SLEW-TO-HOT-TARGET-NORTH"]

    for k in ["dataURI", "dataURL"]:
        col = res[k].tolist()
        for i, val in enumerate(col):
            _v = val.replace("_cal.fits", "_rate.fits").replace("_rateints", "_rate")
            _v = _v.replace("_uncal.fits", "_rate.fits")
            _v = _v.replace("_trapsfilled.fits", "_rate.fits")

            col[i] = _v

        res.remove_column(k)
        res[k] = col

    un = utils.Unique(res["dataURL"], verbose=False)

    keep = res["exptime"] > 0

    for i in np.where(np.array(un.counts) > 1)[0]:
        vi = un.values[i]
        j = np.where(un[vi])[0][1:]
        keep[j] = False

    mask_mode = utils.column_string_operation(
        res["inst-mode"],
        [
            "MASK",
            "WLP",
            "FND",
            "P750L",
            "1065C",
            "2100C",
            "2300C",
            "1550C",
            "1140C",
            #'GR1','GRIS',
            #'W2',
            "GR700",
            # 'MP','WP',  # NIRISS long
            "NRM",
            "xF212N",
        ],
        method="count",
    )
    keep &= ~mask_mode

    keep &= ~np.isin(
        res["scicat"], ["Solar System Astronomy", "Exoplanets and Exoplanet Formation"]
    )

    if 0:
        keep &= res["instrument_name"] == "NIRCAM"

    print(len(res), keep.sum())
    ores = res[~keep]
    res = res[keep]
    
    print(f"Imaging: {len(res)} rows")
    
    res.write("../../../assets/dashboard/imaging.csv", overwrite=True)
    
    if len(res) > 0:
        with open("imaging.md","w") as fp:
            fp.write(f"""
xxx query: *{now_iso[:len("2025-09-01 01:18")]} ± {dt} days*

""".replace("xxx","[imaging.csv]( {{ site.baseurl }}{% link assets/dashboard/imaging.csv %} )"))
            fp.write(query_summary(res).to_pandas().to_markdown(index=False))


def dashboard_mirispec():
    ### MIRI Spectroscopy
    extra_filters = []

    extra_filters += mastquery.jwst.make_query_filter(
        "exp_type", values=["MIR_LRS-FIXEDSLIT", "MIR_MRS"]
    )

    extra_filters += mastquery.jwst.make_query_filter(
        "instrume", values=["MIRI"]
    )

    extra_filters += mastquery.jwst.make_query_filter(
        "productLevel",
        values=["3"],
    )

    # Public
    extra_filters += mastquery.jwst.make_query_filter(
        "publicReleaseDate_mjd", range=[now - dt, now + dt]
    )

    extensions = ["rate", "uncal", "cal", 's2d','s3d']

    query = []

    print("Query: ")
    for q in query + extra_filters:
        print(q)

    res = mastquery.jwst.query_jwst(
        instrument="MIR",
        filters=query + extra_filters,
        extensions=extensions,
        # recent_days=2000,
        rates_and_cals=False,
    )


    # Unique rows
    rates = []
    unique_indices = []

    skip = np.isin(res["filter"], ["OPAQUE"])
    skip |= np.isin(
        res["scicat"], ["Solar System Astronomy", "Exoplanets and Exoplanet Formation"]
    )

    if "is_imprt" in res.colnames:
        for j, imp in enumerate(res["is_imprt"]):
            skip[j] |= imp == "t"
 
    if skip.sum() > 0:
        print(f"Remove {skip.sum()} rows")
        res = res[~skip]

    res["release"] = astropy.time.Time(res["publicReleaseDate_mjd"], format="mjd").iso

    res["observed"] = astropy.time.Time(res["expstart"], format="mjd").iso

    so = np.argsort(res["publicReleaseDate_mjd"])
    res = utils.GTable(res[so])

    un = utils.Unique(res["filename"], verbose=False)
    res = res[un.unique_index(0)]

    so = np.argsort(res["date_beg_mjd"])
    res = utils.GTable(res[so])
    
    mode = []
    for i, row in enumerate(res):
        if row['exp_type'] == 'MIR_LRS-FIXEDSLIT':
            mode.append(row['filter'])
        else:
            mode.append('{channel}{band}'.format(**row["channel","band"])[:2])

    res['filter-pupil'] = mode

    print(f"MIRI spec: {len(res)} rows")
    
    res.write("../../../assets/dashboard/mirispec.csv", overwrite=True)

    if len(res) > 0:
        with open("mirispec.md","w") as fp:
            fp.write(f"""
xxx query: *{now_iso[:len("2025-09-01 01:18")]} ± {dt} days*

""".replace("xxx","[mirispec.csv]( {{ site.baseurl }}{% link assets/dashboard/mirispec.csv %} )"))
            fp.write(query_summary(res).to_pandas().to_markdown(index=False))


if __name__ == "__main__":
    
    dashboard_nirspec()
    dashboard_imaging()
    dashboard_mirispec()

    