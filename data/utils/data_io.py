import os
import json
import numpy as np
import pandas as pd

diagnosis_priority_dict = {
    '': 0,
    'Primary': 1,
    'Major': 2,
    'Other': 3,
}


def load_patient_data_by_id(patient_id):
    return json.load(open('/media/kai/Shared Space/database-ICU/eICU/all/' + str(patient_id) + '.json'))  # noqa


def load_processed_patient_data_by_id(patient_id):
    patient_data = pd.read_csv(
        'processed_dataset/all/data/'+str(patient_id)+'.csv', sep='\t', header=0)  # noqa
    patient_info = pd.read_csv(
        'processed_dataset/all/info/'+str(patient_id)+'.csv', sep='\t', header=0)  # noqa
    return patient_info, patient_data


def save_csv(path, data: pd.DataFrame):
    save_dir, file_name = os.path.split(path)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    data.to_csv(path, na_rep='', sep='\t', index=False)
    return 1


def print_patient_data(data, max_num=10):
    for k in data:
        print(f'\n{k}:')
        for kk in data[k]:
            print(f'\t{kk}, {data[k][kk][:max_num]}')


def select_entry_subset(dictionary,
                        entry_group='intakeoutput',
                        entry='celllabel',
                        entry_name='Urine'):
    subset_idx = np.where(
        np.array(dictionary[entry_group][entry]) == entry_name)
    return subset_idx


def select_list_subset_with_index(x, idx):
    arr = np.array(x)
    return arr[idx].tolist()


def valid_data_length(data: list):
    data = [d for d in data if d is not None and d == d]
    return len(data)


def convert_lab_data_to_num(d):
    if d == '':
        return np.nan
    elif '<' in d:
        return float(d.replace('<', ''))
    elif '>' in d:
        return float(d.replace('>', ''))
    elif '%' in d:
        return float(d.replace('%', ''))
    else:
        return float(d)


drugrate_unit_dict = {
    'mcg/min': 1 / 1000,
    'mcg/hr': 1 / 60 / 1000,
    'mcg/kg/min': 1 / 1000,
    'mcg/kg/hr': 1 / 60 / 1000,

    'mg/min': 1 / 1000,
    'mg/hr': 1 / 60 / 1000,
    'mg/kg/min': 1 / 1000,
    'mg/kg/hr': 1 / 60 / 1000,

    'units/min': 1,
    'units/hr': 1 / 60,

    'ml/min': 1,
    'ml/hr': 1 / 60,
}

unitID_dict = {
    'mcg/hr': 101,
    'mcg/kg/hr': 102,
    'mcg/kg/min': 103,
    'mcg/min': 104,
    'mg/hr': 105,
    'mg/kg/min': 106,
    'mg/min': 107,
    'units/hr': 108,
    'units/min': 109,
    'ml/hr': 200,
}


def unify_drugrate_unit(rate, name, weight):
    for k in drugrate_unit_dict:
        if k in name:
            if weight == '':
                weight = 1
            else:
                weight = float(weight)
            return float(rate) * weight * drugrate_unit_dict[k], unitID_dict[k]


# Check if a measurement/signal exist in patient data during the time window
# before the target diagnosis event
def sig_exist(sig_uid, data: pd.DataFrame, t_dx, window_size=1440):
    # sig_uid: unique ID of signal source (see DatasetOverview)
    # data: preprocessed patient data
    # t_dx: event time of the target diagnosis
    # window_size: time window before the target diagnosis
    sig_data = data[data['UID'] == sig_uid]
    if sig_data.shape[0] == 0:
        return sig_data

    sig_data_before_event = sig_data[
        (sig_data['Offset'] > 0)
        & (sig_data['Offset'] < t_dx)
        & (sig_data['Offset'] > t_dx - window_size)
    ]
    return sig_data_before_event
