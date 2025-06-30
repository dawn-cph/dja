import os
import yaml
import glob
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

    def __init__(self, text=None, file=None, cycle=3, **kwargs):
        self.cycle = cycle
        self.file = file
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


def parse_schedule_file(schedule_file="20250210_report_20250211.txt", cycle=3, verbose=True, read_json=True):
    """
    Read a schedule file and parse data
    """
    json_file = os.path.join(f'Cycle{cycle}', schedule_file.replace(".txt", ".json"))
    if os.path.exists(json_file) and read_json:
        with open(json_file) as fp:
            elist = json.load(fp)

        print(f"Read {len(elist)} entries from {json_file}")
        return elist

    lines = read_raw_schedule(schedule_file=schedule_file)
    
    # Header
    for i, line in enumerate(lines):
        if line.startswith('---'):
            break

    entries = []
    for line in lines[i+1:]:
        if len(line.strip()) == 0:
            continue

        entry = ScheduleEntry(text=line, file=schedule_file, cycle=cycle)
        if entry.visit_type.strip() == '':
            # Multiple targets?
            last_entry.target += ", " + entry.target
        elif 'PARALLEL' in entry.visit_type:
            last_entry.parallels.append(entry.__dict__)
        else:
            last_entry = entry
            entries.append(entry)
    
    print(f"Read {len(entries)} schedule entries from {schedule_file}")
    elist = [e.__dict__ for e in entries]

    with open(json_file, "w") as fp:
        json.dump(elist, fp)

    return elist


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


def schedule_file_to_markdown(schedule_file="20250217_report_20250214.txt", cycle=3):
    """
    """
    
    header = """\n\n### <a href="{BASE_URL}/{schedule_file}" > {schedule_file} </a>

|  Date  |  Time   | Program | Visit | Duration | Intrument | Target | Keywords | 
| :----: | :-----: | :-----: | ----: | :------: | :-------- | :----- | :------- |
"""

    primary_line = "| {split_time}  | <a href=\"https://www.stsci.edu/jwst-program-info/program/?program={program}\"> {program} </a> | {visit:>3}:{observation:<2} |  {duration_string}  | {instrument:<36}  | {target:<43}  |  {keys:<48} |"

    pure_line = "|  |  | <a href=\"https://www.stsci.edu/jwst-program-info/program/?program={program}\"> {program} </a> | {visit:>3}:{observation:<2} |  |  {instrument:<36}  | Pure Parallel  |   |"

    coord_line = "|  |  |  |   |  |  {instrument:<36}  | Coordinated Parallel  |   |"

    calib_line = "|  |  | <a href=\"https://www.stsci.edu/jwst-program-info/program/?program={program}\"> {program} </a> | {visit:>3}:{observation:<2} |  |  {instrument:<36}  | Internal Calibration  |   |"

    text_lines = []
    entries = parse_schedule_file(schedule_file=schedule_file, cycle=cycle)

    text_lines.append(header.format(BASE_URL=BASE_URL, schedule_file=schedule_file))

    for e in entries[::-1]:
        # e = entry.__dict__
        keys = e["keywords"].split(',')
        if len(keys) > 3:
             keys = keys[:3] + ["..."]
        
        e["keys"] = ", ".join(keys)
        
        duration_string = get_duration_string(e["duration"])
        
        text_lines.append(
            primary_line.format(
                duration_string=duration_string,
                split_time=e["start_time"][:-1].replace('T', ' | ').replace('-','.'),
                **e
            ) + "\n"
        )

        if len(e["parallels"]) > 0:
            for p in e["parallels"]:
                if 'PURE' in p["visit_type"]:
                    text_lines.append(pure_line.format(**p) + "\n")
                elif "CALIB" in p["visit_type"]:
                    text_lines.append(calib_line.format(**p) + "\n")
                else:
                    text_lines.append(coord_line.format(**p) + "\n")
    
    repl = {
        'Wide Field Slitless Spectroscopy': 'WFSS',
        'Single-Object Slitless Spectroscopy': 'SOSS',
        'IFU Spectroscopy': 'IFU',
        'Fixed Slit Spectroscopy': 'Fixed Slit',
        'Low Resolution Spectroscopy': 'LRS slit',
        'Medium Resolution Spectroscopy': 'MRS IFU',
    }

    cycle = entries[0]["cycle"]
    md_file = os.path.join(f'Cycle{cycle}', schedule_file.replace(".txt", ".md"))

    with open(md_file,"w") as fp:
        for line in text_lines:
            for rk in repl:
                line = line.replace(rk, repl[rk])
                
            fp.write(line)

    return entries, text_lines


def read_schedule_summary(url="https://www.stsci.edu/jwst/science-execution/observing-schedules.html"):
    """
    """
    http = urllib3.PoolManager()
    
    print(f'Fetch raw schedule from {url}')
    
    response = http.request('GET', url)
    data = response.data.decode('utf-8').split("\n")
    
    schedule_files = {}
    
    for i, line in enumerate(data):
        if "accordion__title-text" in line:
            cycle = line.split(">")[1].split("<")[0].replace(' ', '')
            print(f"Row {i} - {cycle}")
            schedule_files[cycle] = []
        elif "_report_" in line:
            schedule_file  = os.path.basename(line.split("<a href")[1].split('"')[1])
            if schedule_file.endswith(".txt"):
                schedule_files[cycle].append(schedule_file)
    
    with open("observing-schedules.yaml", "w") as fp:
        yaml.dump(schedule_files, fp)

    return schedule_files


def make_merged_json():
    """
    """
    for cycle in [1,2,3,4]:
        files = glob.glob(f"Cycle{cycle}/*json")
        print(f"Make merged Cycle {cycle} json file from N={len(files)} separate files")
        entries = []
        for file in files:
            with open(file) as fp:
                entries += json.load(fp)
        
        timestamps = [e['start_time'] for e in entries]
        so = np.argsort(timestamps)
        sorted_entries = [entries[i] for i in so]
        
        with open(f'jwst-schedule-cycle{cycle}.json', 'w') as fp:
            json.dump(sorted_entries, fp)


def schedules_to_markdown(markdown_file="jwst_schedules.md", cycles=[4]):
    """
    """

    with open("observing-schedules.yaml") as fp:
        schedule_files = yaml.load(fp, Loader=yaml.Loader)
        
    all_entries = {}
    
    post_header = """---
layout: page
title: JWST Schedules
showGeneral: true
navigation_weight: 12
---

Reformatted views of the JWST Observing Schedules <a href="https://www.stsci.edu/jwst/science-execution/observing-schedules">posted by STScI</a>.

Table created with the script <a href="../../assets/schedule/"> here </a>.

Schedules from previous cycles <a href="../jwst_schedules_past_cycles/#cycle-1"> 1 </a>
, <a href="../jwst_schedules_past_cycles/#cycle-2"> 2 </a>, and <a href="../jwst_schedules_past_cycles/#cycle-3"> 3 </a>.

JSON files with full parsed schedule entries:
<a href="../../assets/schedule/jwst-schedule-cycle4.json"> jwst-schedule-cycle4.json </a>,
<a href="../../assets/schedule/jwst-schedule-cycle3.json"> jwst-schedule-cycle3.json </a>,
<a href="../../assets/schedule/jwst-schedule-cycle2.json"> jwst-schedule-cycle2.json </a>,
<a href="../../assets/schedule/jwst-schedule-cycle1.json"> jwst-schedule-cycle1.json </a>.

"""
    text_lines = [post_header]
    
    for cycle in cycles:
        key = f"Cycle{cycle}"
        if key in schedule_files:
            print(f"\n {key} \n")
            if not os.path.exists(key):
                os.mkdir(key)

            text_lines.append(f"\n## Cycle {cycle}\n")

            schedules = schedule_files[key]
            for schedule_file in schedules:
                md_file = os.path.join(f'Cycle{cycle}', schedule_file.replace(".txt", ".md"))
                if not os.path.exists(md_file):
                    entries, _lines = schedule_file_to_markdown(
                        schedule_file=schedule_file,
                        cycle=cycle
                    )

                print(f"Read markdown from {md_file}")
                with open(md_file) as fp:
                    _lines = fp.readlines()

                text_lines += _lines

    repl = {
        'Wide Field Slitless Spectroscopy': 'WFSS',
        'Single-Object Slitless Spectroscopy': 'SOSS',
        'IFU Spectroscopy': 'IFU',
        'Fixed Slit Spectroscopy': 'Fixed Slit',
        'Low Resolution Spectroscopy': 'LRS slit',
        'Medium Resolution Spectroscopy': 'MRS IFU',
        'MultiObject Spectroscopy': 'MOS',
    }

    with open(markdown_file,"w") as fp:
        # fp.writelines(text_lines)
        for line in text_lines:
            for rk in repl:
                line = line.replace(rk, repl[rk])
                
            fp.write(line)

    make_merged_json()
    
    return all_entries


if __name__ == "__main__":

    read_schedule_summary()

    schedules_to_markdown(markdown_file="../../general/jwst_schedules.md")

    