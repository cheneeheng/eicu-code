"""
Clean up the raw dataset from EICU and generate 2 structured data /data.


1. Patient info. {'UID', 'Value'}
- patient data at admission and discharge.

2. Patient data. {'UID', 'Value', 'Unit', 'Offset'}
- patient data during admission.
- only takes the entries found in `DATA_MAPPING_TSV_FILE`
- removes entries with NAN or None.
- removes duplicates.
- skips diagnosis entries where the name is ''
- skips infusion entries where the value is ''
- skips infusion entries where weight is not available.

For (2.) we take the following tables:
# 5.2. periodic and aperiodic vitals ---------------------------
# 5.3. intake & output -----------------------------------------
# 5.4. lab -----------------------------------------------------
# 5.5. infusion drug -------------------------------------------
# 5.6. nurse charting ------------------------------------------
# 5.7. diagnosis -----------------------------------------------

* medication is not used because they represent drugs ordered,
  and not administered (can be found in infusion drug).

"""

import math
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, RLock

from projects.data_cleaning import *


def create_data_table(dtype=float):
    return {
        'Offset': np.array([], dtype=int),
        'UID': np.array([], dtype=int),
        'Value': np.array([], dtype=dtype),
        'Unit': np.array([], dtype='<U32'),
    }


def concatenate_data_table(x: dict, y: dict):
    return {
        'Offset': np.concatenate([x['Offset'], y['Offset']]),
        'UID': np.concatenate([x['UID'], y['UID']]),
        'Value': np.concatenate([x['Value'], y['Value']]),
        'Unit': np.concatenate([x['Unit'], y['Unit']]),
    }


def sort_data_table(x: dict):
    sorted_ids = np.argsort(x['Offset'])
    for k in x.keys():
        x[k] = x[k][sorted_ids]


def append_to_data_table(x: dict,
                         offset=None,
                         uid=None,
                         value=None,
                         unit=None):
    if offset is None:
        raise ValueError("Offset is None")
    if isinstance(offset, list) and len(offset) == 0:
        return
    x['Offset'] = np.append(x['Offset'], offset)
    x['UID'] = np.append(x['UID'], uid)
    x['Value'] = np.append(x['Value'], value)
    x['Unit'] = np.append(x['Unit'], unit)


def remove_duplicates_in_data_table(x: dict):
    stacked_arr = np.stack(
        [x['Offset'], x['UID'], x['Value'], x['Unit']]).astype(str)
    stacked_arr = np.unique(stacked_arr, axis=1)
    x['Offset'] = stacked_arr[0].astype(x['Offset'].dtype)
    x['UID'] = stacked_arr[1].astype(x['UID'].dtype)
    x['Value'] = stacked_arr[2].astype(x['Value'].dtype)
    x['Unit'] = stacked_arr[3].astype(x['Unit'].dtype)


def remove_null_value_in_data_table(x: dict):
    non_null_mask = ~pd.isnull(x['Value'])
    for k in x:
        x[k] = x[k][non_null_mask]


def create_patient_info(dtype=float):
    return {
        'UID': np.array([], dtype=int),
        'Value': np.array([], dtype=dtype),
    }


def sort_patient_table(x: dict):
    sorted_ids = np.argsort(x['UID'])
    for k in x.keys():
        x[k] = x[k][sorted_ids]


def unify_drugrate_unit(drugrate: float, drugname: str, patientweight: float):
    convert_coeff = 1
    unit = None
    for k in UNIT_CONVERSION_DICT:
        if k in drugname:
            unit = k
            convert_coeff = UNIT_CONVERSION_DICT[k]
            if 'kg' in drugname:
                if patientweight == -1.0:
                    raise ValueError("Patient weight is invalid.")
                convert_coeff *= patientweight
            break
    return drugrate * convert_coeff, unit


def get_patient_weights(data, patient_weights):
    assert isinstance(patient_weights, list)

    if data['patient']['admissionweight'][0] is not None:
        patient_weights += data['patient']['admissionweight']

    if data['patient']['dischargeweight'][0] is not None:
        patient_weights += data['patient']['dischargeweight']

    if "flowsheet|Flowsheet Cell Labels|I&O|Weight|Bodyweight (kg)" in \
            data['intakeOutput']['cellpath']:
        entry_sub_ids = select_entry_subset(
            data, 'intakeOutput', 'cellpath',
            "flowsheet|Flowsheet Cell Labels|I&O|Weight|Bodyweight (kg)")[0]
        entry_values = select_list_subset_with_index(
            data['intakeOutput']['cellvaluenumeric'],
            entry_sub_ids
        )
        patient_weights += entry_values

    if "flowsheet|Flowsheet Cell Labels|I&O|Weight|Bodyweight (lb)" in \
            data['intakeOutput']['cellpath']:
        entry_sub_ids = select_entry_subset(
            data, 'intakeOutput', 'cellpath',
            "flowsheet|Flowsheet Cell Labels|I&O|Weight|Bodyweight (lb)")[0]
        entry_values = select_list_subset_with_index(
            data['intakeOutput']['cellvaluenumeric'],
            entry_sub_ids
        )
        patient_weights += [i * 0.453592 for i in entry_values]

    return patient_weights


def check_patient_height_weight(check: dict):
    # sanity check based on the sql in "concepts".
    assert check['admissionheight'] is not None
    assert check['admissionweight'] is not None

    weight = check['admissionweight'][1]
    height = check['admissionheight'][1]

    if check['admissionweight'][1] is not None and \
            check['admissionheight'][1] is not None:

        if check['admissionweight'][1] >= 100 and \
                check['admissionheight'][1] > 25 and \
                check['admissionheight'][1] <= 100 and \
                abs(check['admissionheight'][1]-check['admissionweight'][1]) >= 20:
            weight = check['admissionheight'][1]
            height = check['admissionweight'][1]

        if weight is not None:
            if weight <= 20:
                weight = None
            elif weight > 300:
                weight = None

        if height is not None:
            if height <= 0.3:
                height = None
            elif height <= 2.5:
                height *= 100
            elif height <= 10:
                height = None
            elif height <= 25:
                height *= 10
            elif height <= 25:
                height *= 10
            elif weight is not None:
                if height <= 100 and abs(height-weight) < 20:
                    height = None
            elif height > 250:
                height = None

    return height, weight


def save_patient_info(data, data_mapping, table_id, table_dict, output):

    # sanity check based on the sql in "concepts".
    check = {
        "admissionheight": None,
        "admissionweight": None
    }

    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]
    for _, entry in entry_mapping.iterrows():
        entry_name_eicu = entry['ParamNameOrigin']
        entry_uid = entry['TableUID']
        if len(data[table_source][entry_name_eicu]) == 1:
            entry_value = data[table_source][entry_name_eicu][0]
        else:
            raise ValueError(len(data[table_source][entry_name_eicu]))

        if entry_name_eicu in check.keys():
            check[entry_name_eicu] = (entry_uid, entry_value)
            continue

        output['UID'] = np.append(output['UID'], entry_uid)
        output['Value'] = np.append(output['Value'], str(entry_value))

    height, weight = check_patient_height_weight(check)
    output['UID'] = np.append(output['UID'], check['admissionheight'][0])
    output['Value'] = np.append(output['Value'], height)
    output['UID'] = np.append(output['UID'], check['admissionweight'][0])
    output['Value'] = np.append(output['Value'], weight)

    sort_patient_table(output)

    return output


def save_periodic_aperiodic_vitals(data, data_mapping, table_id, table_dict,
                                   output):
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]

    _output = create_data_table()
    for _, entry in entry_mapping.iterrows():
        entry_name_eicu = entry['ParamNameOrigin']
        entry_uid = entry['TableUID']
        entry_offset = data[table_source]['observationoffset']
        entry_vals = data[table_source][entry_name_eicu]

        append_to_data_table(_output,
                             offset=entry_offset,
                             uid=[entry_uid] * len(entry_offset),
                             value=entry_vals,
                             unit=[None] * len(entry_offset))

    remove_null_value_in_data_table(_output)
    remove_duplicates_in_data_table(_output)
    sort_data_table(_output)
    _output = concatenate_data_table(output, _output)
    return _output


def save_intake_output(data, data_mapping, table_id, table_dict, output):
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]
    # intakeoutputoffset shared by :
    # [intaketotal, outtaketotal, dialysistotal, nettotal]

    # 1. pure fluid intake output.
    _output1 = create_data_table()
    _iter = entry_mapping[entry_mapping['TableUID'] < 300005].iterrows()
    for _, entry in _iter:
        entry_name_eicu = entry['ParamNameOrigin']
        entry_uid = entry['TableUID']
        entry_offset = data[table_source]['intakeoutputoffset']
        entry_vals = data[table_source][entry_name_eicu]

        append_to_data_table(_output1,
                             offset=entry_offset,
                             uid=[entry_uid] * len(entry_offset),
                             value=entry_vals,
                             unit=[None] * len(entry_offset))

    remove_null_value_in_data_table(_output1)
    remove_duplicates_in_data_table(_output1)
    sort_data_table(_output1)
    _output = concatenate_data_table(output, _output1)

    # 2. other individual intake-output entries
    uid_dict = entry_mapping[['ParamNameOrigin', 'TableUID']]
    uid_dict = {uid_dict.iloc[i, 0]: uid_dict.iloc[i, 1]
                for i in range(uid_dict.shape[0])}
    _output2 = create_data_table()
    for i, entry_name_eicu in enumerate(data[table_source]['cellpath']):
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_offset = data[table_source]['intakeoutputoffset'][i]
            entry_value = data[table_source]['cellvaluenumeric'][i]

            if entry_name_eicu == "flowsheet|Flowsheet Cell Labels|I&O|Weight|Bodyweight (lb)":
                entry_uid -= 1
                entry_value *= 0.453592

            append_to_data_table(_output2,
                                 offset=entry_offset,
                                 uid=entry_uid,
                                 value=entry_value,
                                 unit=None)

    remove_null_value_in_data_table(_output2)
    remove_duplicates_in_data_table(_output2)
    sort_data_table(_output2)
    _output = concatenate_data_table(output, _output2)
    return _output


def save_lab_results(data, data_mapping, table_id, table_dict, output):
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]
    uid_dict = entry_mapping[['ParamNameOrigin', 'TableUID']]
    uid_dict = {uid_dict.iloc[i, 0]: uid_dict.iloc[i, 1]
                for i in range(uid_dict.shape[0])}

    _output = create_data_table()
    for i, entry_name_eicu in enumerate(data[table_source]['labname']):
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_offset = data[table_source]['labresultoffset'][i]
            entry_value = data[table_source]['labresulttext'][i]
            # convert lab data to float type
            entry_value = convert_lab_data_to_num(entry_value)

            append_to_data_table(_output,
                                 offset=entry_offset,
                                 uid=entry_uid,
                                 value=entry_value,
                                 unit=None)

    remove_null_value_in_data_table(_output)
    remove_duplicates_in_data_table(_output)
    sort_data_table(_output)
    _output = concatenate_data_table(output, _output)
    return _output


def save_infusion_drug_info(data, data_mapping, table_id, table_dict, output):
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]

    # take the patient weight in the infusion table
    # if the length of entry is the same as infusion drugs,
    # or else take the average of admission and discharge weight.
    patient_weights = []
    entry_len = len(data[table_source]['drugname'])
    valid_len = len([i for i in data[table_source]
                    ['patientweight'] if i != ''])
    if valid_len != entry_len:
        patient_weights = get_patient_weights(data, patient_weights)
        if len(patient_weights) == 0:
            patient_weights = [-1.0]
            # raise ValueError("No weight available")
        assert None not in patient_weights, patient_weights
        patient_weights = [float(i) for i in patient_weights]
        patient_weights = [sum(patient_weights) / len(patient_weights)]
        patient_weights = patient_weights * len(data[table_source]['drugname'])

    else:
        patient_weights = [float(i)
                           for i in data[table_source]['patientweight']]

    uid_dict = entry_mapping[['ParamNameOrigin', 'TableUID']]
    uid_dict = {uid_dict.iloc[i, 0]: uid_dict.iloc[i, 1]
                for i in range(uid_dict.shape[0])}

    _output = create_data_table()
    for i, entry_name_eicu in enumerate(data[table_source]['drugname']):
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_offset = data[table_source]['infusionoffset'][i]
            entry_value = data[table_source]['drugrate'][i]
            if entry_value == '':
                continue
            entry_weight = patient_weights[i]
            if entry_weight < 0.0:
                continue
            # unify drugrate unit to: mg/min, units/min, ml/min
            entry_value, entry_unit = unify_drugrate_unit(
                drugname=entry_name_eicu,
                drugrate=-1.0 if entry_value == 'OFF' else float(entry_value),
                patientweight=entry_weight
            )

            append_to_data_table(_output,
                                 offset=entry_offset,
                                 uid=entry_uid,
                                 value=entry_value,
                                 unit=entry_unit)

    remove_null_value_in_data_table(_output)
    remove_duplicates_in_data_table(_output)
    sort_data_table(_output)
    _output = concatenate_data_table(output, _output)
    return _output


def save_nurse_charting(data, data_mapping, table_id, table_dict, output):
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]

    _output = create_data_table()
    for _, entry in entry_mapping.iterrows():
        entry_name_eicu = entry['ParamNameOrigin']
        entry_label_eicu = entry['ParamLabel']
        entry_uid = entry['TableUID']

        entry_sub_ids = select_entry_subset(data,
                                            table_source,
                                            'nursingchartcelltypevalname',
                                            entry_name_eicu)[0]
        entry_sub_ids = entry_sub_ids[
            np.in1d(
                entry_sub_ids,
                select_entry_subset(data,
                                    table_source,
                                    'nursingchartcelltypevallabel',
                                    entry_label_eicu)[0],
            )
        ]

        entry_offsets = select_list_subset_with_index(
            data[table_source]['nursingchartentryoffset'],
            entry_sub_ids
        )
        entry_values = select_list_subset_with_index(
            data[table_source]['nursingchartvalue'],
            entry_sub_ids
        )

        if entry_name_eicu == 'Temperature (F)':
            entry_uid -= 1
            entry_values = [(float(e)-32)/1.8 for e in entry_values]

        append_to_data_table(_output,
                             offset=[int(e) for e in entry_offsets],
                             uid=[entry_uid] * len(entry_offsets),
                             value=entry_values,
                             unit=[None] * len(entry_offsets))

    remove_null_value_in_data_table(_output)
    remove_duplicates_in_data_table(_output)
    sort_data_table(_output)
    _output = concatenate_data_table(output, _output)
    return _output


def save_diagnosis_info(data, data_mapping, table_id, table_dict, output):
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]

    uid_dict = entry_mapping[['ParamNameOrigin', 'TableUID']]
    uid_dict = {uid_dict.iloc[i, 0]: uid_dict.iloc[i, 1]
                for i in range(uid_dict.shape[0])}

    entry_offsets = data[table_source]['diagnosisoffset']
    entry_names = data[table_source]['icd9code']
    # entry_names = data[table_source]['diagnosisstring']
    entry_values = data[table_source]['diagnosispriority']

    _output = create_data_table()
    for entry_offset, entry_name_eicu, entry_value in zip(
            entry_offsets, entry_names, entry_values):
        if entry_name_eicu == '':
            continue
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_value = DIAGNOSIS_PRIORITY_DICT[entry_value]
            append_to_data_table(_output,
                                offset=entry_offset,
                                uid=entry_uid,
                                value=entry_value,
                                unit=None)

    remove_null_value_in_data_table(_output)
    remove_duplicates_in_data_table(_output)
    sort_data_table(_output)
    _output = concatenate_data_table(output, _output)
    return _output


def generate_structured_output(output_folder, table_dict, data_mapping,
                               paid_list, pid=0):

    pbar = tqdm(paid_list, position=pid+1)
    for paid in pbar:

        pbar.set_description(f"Processing {paid}")

        data = load_patient_data_by_id(DATA_CLEANING_INPUT_FOLDER, paid)

        data_table = create_data_table(dtype=int)
        patient_info = create_patient_info(dtype=int)

        # 5. Loop through each data table.
        for table_id in table_dict.keys():

            # 5.1. patient information -----------------------------------------
            if table_id == 0:
                kwargs = {
                    'data': data,
                    'data_mapping': data_mapping,
                    'table_id': table_id,
                    'table_dict': table_dict,
                    'output': patient_info
                }
                patient_info = save_patient_info(**kwargs)

            else:
                kwargs = {
                    'data': data,
                    'data_mapping': data_mapping,
                    'table_id': table_id,
                    'table_dict': table_dict,
                    'output': data_table
                }
                # 5.2. periodic and aperiodic vitals ---------------------------
                if table_id in [1, 2]:
                    data_table = save_periodic_aperiodic_vitals(**kwargs)
                # 5.3. intake & output -----------------------------------------
                elif table_id == 3:
                    data_table = save_intake_output(**kwargs)
                # 5.4. lab -----------------------------------------------------
                elif table_id == 4:
                    data_table = save_lab_results(**kwargs)
                # 5.5. infusion drug -------------------------------------------
                elif table_id == 5:
                    data_table = save_infusion_drug_info(**kwargs)
                # 5.6. nurse charting ------------------------------------------
                elif table_id == 6:
                    data_table = save_nurse_charting(**kwargs)
                # 5.7. diagnosis -----------------------------------------------
                elif table_id == 7:
                    data_table = save_diagnosis_info(**kwargs)

        # save data to csv
        df_info = pd.DataFrame(patient_info)
        df_data = pd.DataFrame(data_table)

        save_dir_info = os.path.join(output_folder, 'info_')+str(paid)+'.dsv'
        save_dir_data = os.path.join(output_folder, 'data_')+str(paid)+'.dsv'
        save_dsv(save_dir_info, df_info)
        save_dsv(save_dir_data, df_data)


def parallel_processing(func, output_folder, table_dict, data_mapping, paid_list=[]):

    def npi(x):
        return math.ceil(len(x) / NUM_PROCESSES)

    num_id_per_process = npi(paid_list)

    argument_list = [
        (output_folder,
         table_dict,
         data_mapping,
         paid_list[pid*num_id_per_process:
                   (pid+1)*num_id_per_process],
         pid)
        for pid in range(NUM_PROCESSES)
    ]

    pool = Pool(processes=NUM_PROCESSES,
                initargs=(RLock(),),
                initializer=tqdm.set_lock)
    jobs = [pool.apply_async(func, args=arg) for arg in argument_list]
    pool.close()
    result_list = [job.get() for job in jobs]
    return result_list


if __name__ == "__main__":

    # if os.path.exists(DATA_CLEANING_OUTPUT_FOLDER):
    #     raise ValueError(
    #         f"The output folder {DATA_CLEANING_OUTPUT_FOLDER} exists!")

    # 1. Load data.
    data_mapping = pd.read_csv(DATA_MAPPING_TSV_FILE, sep='\t', header=0)
    paid_list = [int(i.split('.')[0])
                 for i in os.listdir(DATA_CLEANING_INPUT_FOLDER)]

    # 2. UID for data table.
    table_dict = data_mapping[['TableID', 'TableSource']]
    table_dict = table_dict.drop_duplicates()
    table_dict = {table_dict.iloc[i, 0]: table_dict.iloc[i, 1]
                  for i in range(table_dict.shape[0])}

    # 3. Save patient data in .CSV file
    # generate_structured_output(paid_list, table_dict, data_mapping)
    def npi(x):
        return math.ceil(len(x) / CHUNKS)

    interval = 1

    for i in range(START, CHUNKS, interval):

        x = npi(paid_list) * i
        y = npi(paid_list) * (i + interval)
        list_i = paid_list[x:y]

        output_folder = os.path.join(DATA_CLEANING_OUTPUT_FOLDER, f'{i}')
        os.makedirs(output_folder, exist_ok=True)

        parallel_processing(generate_structured_output, output_folder,
                            table_dict, data_mapping, list_i)

        print("Finished chunk {}/{}".format(i+1, CHUNKS))
