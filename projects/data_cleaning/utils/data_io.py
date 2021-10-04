import os
import json
import numpy as np
import pandas as pd


def load_patient_data_by_id(patient_json_folder, patient_id):
    with open(os.path.join(patient_json_folder, str(patient_id) + '.json')) as f:  # noqa
        json_dict = json.load(f)
    return json_dict


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
    return np.array(x)[idx].tolist()


def valid_data_length(data: list):
    data = [d for d in data if d is not None and d == d]
    return len(data)


def convert_lab_data_to_num(d: str):
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
