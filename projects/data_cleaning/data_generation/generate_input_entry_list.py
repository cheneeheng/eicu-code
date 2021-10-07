"""
Generate a list of all the available diagnosis in the raw data.
"""

import csv
import numpy as np
import os
import json
from tqdm import tqdm


def generate_all_inputs():
    jd_dict = {}
    jd_dict['intakeOutput'] = []
    jd_dict['lab'] = []
    jd_dict['infusionDrug'] = []
    jd_dict['nurseCharting'] = []
    jd_dict['diagnosis'] = []

    pbar = tqdm(os.listdir("outputs/all"))
    for i in pbar:
        jd = json.load(open("outputs/all" + "/" + i, 'r'))
        jd_dict['intakeOutput'] += [i.split("|I&O|")[-1]
                                    for i in jd['intakeOutput']['cellpath']]
        jd_dict['lab'] += [i for i in jd['lab']['labname']]
        jd_dict['infusionDrug'] += [i for i in jd['infusionDrug']['drugname']]
        jd_dict['nurseCharting'] += [
            f"{i}|{j}|{k}"
            for i, j, k in zip(
                jd['nurseCharting']['nursingchartcelltypecat'],
                jd['nurseCharting']['nursingchartcelltypevallabel'],
                jd['nurseCharting']['nursingchartcelltypevalname'])
        ]
        jd_dict['diagnosis'] += [i for i in jd['diagnosis']['diagnosisstring']]

    jd_dict['patient'] = sorted(list(jd['patient'].keys()))
    jd_dict['vitalPeriodic'] = sorted(list(jd['vitalPeriodic'].keys()))
    jd_dict['vitalAperiodic'] = sorted(list(jd['vitalAperiodic'].keys()))

    jd_dict['intakeOutput'] = sorted(set(jd_dict['intakeOutput']))
    jd_dict['lab'] = sorted(set(jd_dict['lab']))
    jd_dict['infusionDrug'] = sorted(set(jd_dict['infusionDrug']))
    jd_dict['nurseCharting'] = sorted(set(jd_dict['nurseCharting']))
    jd_dict['diagnosis'] = sorted(set(jd_dict['diagnosis']))

    output_json_path = 'projects/data_cleaning/resources/input_entry_list.json'
    assert not os.path.exists(output_json_path)
    with open(output_json_path, 'w+') as f:
        json.dump(jd_dict, f)


def generate_intake_output_input():
    jd_dict = {}
    jd_dict['intakeOutput'] = []

    pbar = tqdm(os.listdir("outputs/all"))
    for i in pbar:
        jd = json.load(open("outputs/all" + "/" + i, 'r'))
        jd_dict['intakeOutput'] += [i.split("|I&O|")[-1]
                                    for i in jd['intakeOutput']['cellpath']]

    u_val, count = np.unique(jd_dict['intakeOutput'], return_counts=True)
    vals = [
        x for _, x in sorted(
            zip(count.tolist(), u_val.tolist()),
            reverse=True)
    ]
    counts = [x for x in sorted(count.tolist(), reverse=True)]

    output_path = 'projects/data_cleaning/resources/intake_output_entry_list.txt'  # noqa

    with open(output_path, 'w+') as f:
        f.write(f"Entry Name$Number of Occurences\n")
        for i, j in zip(vals, counts):
            f.write(f"{i}${j}\n")

    # with open(output_path, 'w+', newline='') as csvfile:
    #     csvwriter = csv.writer(csvfile, delimiter=',')
    #     #    quotechar='?', quoting=csv.QUOTE_MINIMAL)
    #     for i, j in zip(vals, counts):
    #         csvwriter.writerow([i, j])


if __name__ == "__main__":
    generate_intake_output_input()
    # generate_all_inputs()
