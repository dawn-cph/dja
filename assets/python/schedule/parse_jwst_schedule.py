import yaml
import urllib3
import json
import matplotlib.pyplot as plt
import numpy as np

BASE_URL = "https://www.stsci.edu/files/live/sites/www/files/home/jwst/science-execution/observing-schedules/_documents"

class ScheduleEntry():
    program = None
    visit = None
    observation = None
    pcs_mode = None
    visit_type = None
    start_time = None
    duration = None
    instrument = None
    target = None
    category = None
    keywords = None
    parallels = []
    
    def __init__(self, text=None, **kwargs):
        if text is not None:
            self.parse_text(text, **kwargs)

    def parse_text(self, text, verbose=False, **kwargs):
        """
        Parse a row from the schedule file
        """
        spl = text.split()
        is_primary = ':' in text.split()[0]

        # "9230:3:1       MOVING      PRIME TARGETED MOVING          2025-02-10T01:57:25Z  00/00:48:27  NIRSpec IFU Spectroscopy                            EUROPA                           Solar System                    Satellite"
        split_index = [0, 15, 27, 58, 80, 93, 145, 178, 210, 1024]
        if is_primary:
            keys = ['pvo', 'pcs_mode', 'visit_type', 'start_time', 'duration', 'instrument', 'target', 'category', 'keywords']
        elif text[:80].strip() == '':
            keys = ['pvo', 'pcs_mode', 'visit_type', 'start_time', 'duration', 'instrument', 'target']
        else:
            keys = ['pvo', 'pcs_mode', 'visit_type', 'start_time', 'duration', 'instrument'] #, 'target', 'category', 'keywords']
                    
        tdict = {}
        for i, key in enumerate(keys):
            sl = slice(split_index[i], split_index[i+1])
            tdict[key] = text[sl].strip()

        if not is_primary:
            tdict['pcs_mode'] = None
            tdict['duration'] = None

        if ':' in tdict['pvo']:
            tdict['program'], tdict['visit'], tdict['observation'] = [
                int(value) for value in tdict['pvo'].split(':')
            ]
        _ = tdict.pop('pvo')
        
        if verbose:
            print(yaml.dump(tdict))

        for k in tdict:
            setattr(self, k, tdict[k])
            # print(f'{attr}: {text[sl].strip()}')

        self.parallels = []
        
    def __repr__(self):
        return "\n### Schedule entry ###\n" + yaml.dump(self.__dict__)


def read_raw_schedule(schedule_file="20250210_report_20250211.txt"):
    """
    """
    http = urllib3.PoolManager()
    
    target_url = f"{BASE_URL}/{schedule_file}"

    print(f'Fetch raw schedule from {target_url}')
    
    response = http.request('GET', target_url)
    data = response.data.decode('utf-8')

    return data.split("\n")


def parse_schedule_file(schedule_file="20250210_report_20250211.txt", verbose=True):
    """
    Read a schedule file and parse data
    """
    lines = read_raw_schedule(schedule_file=schedule_file)
    
    # Header
    for i, line in enumerate(lines):
        if line.startswith('---'):
            break

    entries = []
    for line in lines[i+1:]:
        if len(line.strip()) == 0:
            continue

        entry = ScheduleEntry(text=line)
        if entry.visit_type.strip() == '':
            # Multiple targets?
            last_entry.target += ", " + entry.target
        elif 'PARALLEL' in entry.visit_type:
            last_entry.parallels.append(entry.__dict__)
        else:
            last_entry = entry
            entries.append(entry)
    
    print(f"Read {len(entries)} schedule entries from {schedule_file}")
    
    return entries


def get_duration_string(duration="00/00:35:38", cmap=plt.cm.PuRd, limits=[0, 15]):
    """
    """
    from matplotlib.colors import to_hex
    hms = [int(value) for value in duration.split("/")[-1].split(":")]
    hours = hms[0] + hms[1] / 60. + hms[2] / 3600.
    cval = np.clip(np.interp(hours, limits, [0,1]), 0.25, 0.8*10./15)
    color_hex = to_hex(cmap(cval))
    
    duration_string = f"<span style=\"color:{color_hex};\"> {duration.split('/')[-1]} </span>"
    return duration_string


def schedules_to_mardown(markdown_file="jwst_schedules.md"):
    """
    """
    with open("schedule_files.txt") as fp:
        schedules = [l.strip() for l in fp.readlines()]

    schedules.sort()

    header = """\n\n### <a href="{BASE_URL}/{schedule_file}" > {schedule_file} </a>
    
|  Date  |  Time   | Program | Visit | Duration | Intrument | Target | Keywords | 
| :----: | :-----: | :-----: | ----: | :------: | :-------- | :----- | :------- |
"""

    primary_line = "| {split_time}  | <a href=\"https://www.stsci.edu/jwst-program-info/program/?program={program}\"> {program} </a> | {visit:>3}:{observation:<2} |  {duration_string}  | {instrument:<36}  | {target:<43}  |  {keys:<48} |"

    pure_line = "|  |  | <a href=\"https://www.stsci.edu/jwst-program-info/program/?program={program}\"> {program} </a> | {visit:>3}:{observation:<2} |  |  {instrument:<36}  | Pure Parallel  |   |"

    coord_line = "|  |  |  |   |  |  {instrument:<36}  | Coordinated Parallel  |   |"
    calib_line = "|  |  | <a href=\"https://www.stsci.edu/jwst-program-info/program/?program={program}\"> {program} </a> | {visit:>3}:{observation:<2} |  |  {instrument:<36}  | Internal Calibration  |   |"

    all_entries = {}
    
    post_header = """---
layout: page
title: JWST Schedules
showGeneral: true
navigation_weight: 12
---

Reformatted views of the JWST Observing Schedules <a href="https://www.stsci.edu/jwst/science-execution/observing-schedules">posted by STScI</a>.

Table created with the script <a href="../../assets/python/schedule/"> here </a>.

"""
    out = [post_header]
        
    for schedule_file in schedules[::-1]:
        entries = parse_schedule_file(schedule_file=schedule_file)
    
        out.append(header.format(BASE_URL=BASE_URL, schedule_file=schedule_file))

        for entry in entries[::-1]:
            e = entry.__dict__
            keys = e["keywords"].split(',')
            if len(keys) > 3:
                 keys = keys[:3] + ["..."]
            
            e["keys"] = ", ".join(keys)
            
            duration_string = get_duration_string(e["duration"])
            
            out.append(
                primary_line.format(
                    duration_string=duration_string,
                    split_time=e["start_time"][:-1].replace('T', ' | ').replace('-','.'),
                    **e
                ) + "\n"
            )
            if len(e["parallels"]) > 0:
                for p in e["parallels"]:
                    if 'PURE' in p["visit_type"]:
                        out.append(pure_line.format(**p) + "\n")
                    elif "CALIB" in p["visit_type"]:
                        out.append(calib_line.format(**p) + "\n")
                    else:
                        out.append(coord_line.format(**p) + "\n")
        
        repl = {
            'Wide Field Slitless Spectroscopy': 'WFSS',
            'Single-Object Slitless Spectroscopy': 'SOSS',
            'IFU Spectroscopy': 'IFU',
            'Fixed Slit Spectroscopy': 'Fixed Slit',
            'Low Resolution Spectroscopy': 'LRS slit',
            'Medium Resolution Spectroscopy': 'MRS IFU',
        }

        with open(markdown_file,"w") as fp:
            for line in out:
                for rk in repl:
                    line = line.replace(rk, repl[rk])
                    
                fp.write(line)
        # all_entries[schedule_file] = [e.__dict__ for e in entries]
    
    return all_entries


if __name__ == "__main__":
    schedules_to_mardown(markdown_file="../../../general/jwst_schedules.md")

    