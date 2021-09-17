"""Clean up the raw dataset from EICU and generate a structured data output."""

import numpy as np
import pandas as pd

from data.common import *
from data.utils.data_io import *
from data.utils.utils import *


def create_data_table():
    return {
        'Offset': np.array([]),
        'UID': np.array([]),
        'Value': np.array([]),
        'Unit': np.array([]),
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
    return x


def append_to_data_table(x: dict,
                         offset=None,
                         uid=None,
                         value=None,
                         unit=None):
    x['Offset'] = np.append(x['Offset'], offset)
    x['UID'] = np.append(x['UID'], uid)
    x['Value'] = np.append(x['Value'], value)
    x['Unit'] = np.append(x['Unit'], unit)
    return x


def create_patient_info():
    return {
        'UID': np.array([]),
        'Value': np.array([]),
    }


# TODO : IS THIS THE RIGHT WAY ???
def unify_drugrate_unit(drugrate: float, drugname: str, patientweight: float):
    convert_coeff = 1
    for k in UNIT_CONVERSION_DICT:
        if k in drugname:
            convert_coeff = UNIT_CONVERSION_DICT[k]
            if 'kg' in drugname:
                convert_coeff *= patientweight
    return drugrate * convert_coeff


def save_patient_info(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]
    for _, entry in entry_mapping.iterrows():
        entry_name_eicu = entry['ParamNameOrigin']
        entry_uid = entry['TableUID']
        if len(data[table_source][entry_name_eicu]) == 1:
            entry_value = data[table_source][entry_name_eicu][0]
        else:
            raise ValueError(len(data[table_source][entry_name_eicu]))

        output['UID'] = np.append(output['UID'], entry_uid)
        output['Value'] = np.append(output['Value'], entry_value)

    return output


def save_periodic_aperiodic_vitals(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa
    # read and sort data array per parameter.
    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]
    table_source = table_dict[table_id]
    sorted_ids = np.argsort(data[table_source]['observationoffset'])
    sorted_offset = np.array(data[table_source]['observationoffset'])[sorted_ids]  # noqa

    _output = create_data_table()
    for _, entry in entry_mapping.iterrows():
        entry_name_eicu = entry['ParamNameOrigin']
        entry_uid = entry['TableUID']
        sorted_vals = np.array(data[table_source][entry_name_eicu])[sorted_ids]

        _output = append_to_data_table(_output,
                                       offset=sorted_offset,
                                       uid=[entry_uid] * len(sorted_offset),
                                       value=sorted_vals,
                                       unit=[np.nan] * len(sorted_offset))

        if np.nan in sorted_vals:
            raise ValueError(entry_name_eicu)

    return concatenate_data_table(output, _output)


def save_intake_output(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa

    entry_mapping = data_mapping[data_mapping['TableID'] == table_id]  # noqa
    table_source = table_dict[table_id]
    # intakeoutputoffset shared by :
    # [intaketotal, outtaketotal, dialysistotal, nettotal]
    sorted_ids = np.argsort(data[table_source]['intakeoutputoffset'])  # noqa
    sorted_offset = np.array(data[table_source]['intakeoutputoffset'])[sorted_ids]  # noqa

    # pure fluid intake output.
    _output = create_data_table()
    for _, entry in entry_mapping[entry_mapping['TableUID'] < 300005].iterrows():  # noqa
        entry_name_eicu = entry['ParamNameOrigin']
        entry_uid = entry['TableUID']
        sorted_vals = np.array(data[table_source][entry_name_eicu])[sorted_ids]  # noqa

        _output = append_to_data_table(_output,
                                       offset=sorted_offset,
                                       uid=[entry_uid] * len(sorted_offset),
                                       value=sorted_vals,
                                       unit=[np.nan] * len(sorted_offset))

    output = concatenate_data_table(output, _output)

    # other intake-output entries
    _output = create_data_table()
    for i, entry_name_eicu in enumerate(data[table_source]['celllabel']):
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_offset = data[table_source]['intakeoutputentryoffset'][i]
            entry_value = data[table_source]['cellvaluenumeric'][i]

            _output = append_to_data_table(_output,
                                           offset=entry_offset,
                                           uid=entry_uid,
                                           value=entry_value,
                                           unit=np.nan)

    return concatenate_data_table(output, sort_data_table(_output))


def save_lab_results(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa
    table_source = table_dict[table_id]
    _output = create_data_table()
    for i, entry_name_eicu in enumerate(data[table_source]['labname']):
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_offset = data[table_source]['labresultoffset'][i]
            entry_value = data[table_source]['labresulttext'][i]
            # convert lab data to float type
            entry_value = convert_lab_data_to_num(entry_value)

            _output = append_to_data_table(_output,
                                           offset=entry_offset,
                                           uid=entry_uid,
                                           value=entry_value,
                                           unit=np.nan)

    return concatenate_data_table(output, sort_data_table(_output))


def save_infusion_drug_info(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa
    table_source = table_dict[table_id]

    # take the patient weight in the infusion table
    # if the length of entry is the same as infusion drugs,
    # or else take the average of admission and discharge weight.
    patient_weights = []
    entry_len = len(data[table_source]['drugname'])
    valid_len = len([i for i in data[table_source]['patientweight'] if i != ''])  # noqa
    if valid_len != entry_len:  # noqa
        if (data['patient']['admissionweight'] is None) and (
            data['patient']['dischargeweight'] is None):  # noqa
            raise ValueError("No weight available")
        if data['patient']['admissionweight'] is not None:
            patient_weights += data['patient']['admissionweight']
        if data['patient']['dischargeweight'] is not None:
            patient_weights += data['patient']['dischargeweight']
        patient_weights = [i.astype(float)for i in patient_weights]
        patient_weights = [sum(patient_weights) / len(patient_weights)]
        patient_weights = patient_weights * len(data[table_source]['drugname'])
    else:
        patient_weights = [i.astype(float) for i in data[table_source]['patientweight']]  # noqa

    _output = create_data_table()
    for i, entry_name_eicu in enumerate(data[table_source]['drugname']):
        if entry_name_eicu in uid_dict:
            entry_uid = uid_dict[entry_name_eicu]
            entry_offset = data[table_source]['infusionoffset'][i]
            entry_value = data[table_source]['drugrate'][i]
            if entry_value == '':
                continue
            entry_weight = patient_weights[i]
            # unify drugrate unit to: mg/min, units/min, ml/min
            entry_value, entry_unit = unify_drugrate_unit(
                drugname=entry_name_eicu,
                drugrate=entry_value.astype(float),
                patientweight=entry_weight
            )

            _output = append_to_data_table(_output,
                                           offset=entry_offset,
                                           uid=entry_uid,
                                           value=entry_value,
                                           unit=entry_unit)

    return concatenate_data_table(output, sort_data_table(_output))


def save_nurse_charting(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa
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

        entry_offset = select_list_subset_with_index(
            data[table_source]['nursingchartentryoffset'],
            entry_sub_ids
        )
        entry_value = select_list_subset_with_index(
            data[table_source]['nursingchartvalue'],
            entry_sub_ids
        )

        _output = append_to_data_table(_output,
                                       offset=entry_offset,
                                       uid=[entry_uid] * len(entry_offset),
                                       value=entry_value,
                                       unit=[np.nan] * len(entry_offset))

    return concatenate_data_table(output, sort_data_table(_output))


def save_diagnosis_info(data, data_mapping, table_id, table_dict, uid_dict, output):  # noqa
    table_source = table_dict[table_id]
    entry_offsets = data[table_source]['diagnosisoffset']
    entry_names = data[table_source]['icd9code']
    entry_values = data[table_source]['diagnosispriority']

    _output = create_data_table()
    for entry_offset, entry_name, entry_value in zip(entry_offsets, entry_names, entry_values):  # noqa
        if entry_name == '':
            continue
        entry_uid = uid_dict[entry_name]
        entry_value = DIAGNOSIS_PRIORITY_DICT[entry_value]
        _output = append_to_data_table(_output,
                                       offset=entry_offset,
                                       uid=entry_uid,
                                       value=entry_value,
                                       unit=np.nan)

    return concatenate_data_table(output, sort_data_table(_output))


if __name__ == "__main__":

    # 1. Load data.
    data_mapping = pd.read_csv(DATA_MAPPING_TSV_FILE, sep='\t', header=0)
    pid_list = [int(i.split('.')[0]) for i in os.listdir(PREPROCESS_INPUT_FOLDER)]  # noqa

    # 2. UID for data table.
    table_dict = data_mapping[['TableID', 'TableSource']]
    table_dict = table_dict.drop_duplicates()
    table_dict = {table_dict.iloc[i, 0]: table_dict.iloc[i, 1]
                  for i in range(table_dict.shape[0])}

    # 3. UID for all parameters.
    uid_dict = data_mapping[['ParamNameOrigin', 'TableUID']]
    uid_dict = {uid_dict.iloc[i, 0]: uid_dict.iloc[i, 1]
                for i in range(uid_dict.shape[0])}

    # 4. Save patient data in .CSV file
    for pid in pid_list:
        data = load_patient_data_by_id(PREPROCESS_INPUT_FOLDER, pid)

        data_table = create_data_table()
        patient_info = create_patient_info()

        # 5. Loop through each data table.
        for table_id in table_dict.keys():

            # 5.1. patient information ----------------------------------------
            if table_id == 0:
                kwargs = {
                    'data': data,
                    'data_mapping': data_mapping,
                    'table_id': table_id,
                    'table_dict': table_dict,
                    'uid_dict': uid_dict,
                    'output': patient_info
                }
                patient_info = save_patient_info(**kwargs)

            else:
                kwargs = {
                    'data': data,
                    'data_mapping': data_mapping,
                    'table_id': table_id,
                    'table_dict': table_dict,
                    'uid_dict': uid_dict,
                    'output': data_table
                }
                # 5.2. periodic and aperiodic vitals --------------------------
                if table_id in [1, 2]:
                    data_table = save_periodic_aperiodic_vitals(**kwargs)
                # 5.3. intake & output ----------------------------------------
                elif table_id == 3:
                    data_table = save_intake_output(**kwargs)
                # 5.4. lab ----------------------------------------------------
                elif table_id == 4:
                    data_table = save_lab_results(**kwargs)
                # 5.5. infusion drug ------------------------------------------
                elif table_id == 5:
                    data_table = save_infusion_drug_info(**kwargs)
                # 5.6. nurse charting -----------------------------------------
                elif table_id == 6:
                    data_table = save_nurse_charting(**kwargs)
                # 5.7. diagnosis ----------------------------------------------
                elif table_id == 7:
                    data_table = save_diagnosis_info(**kwargs)

        data_table = kwargs['output']
        
        # All previous valid data (non zero) + diagnosis.
        mask = np.logical_or(
            np.logical_and(data_table['UID'] < 7e5, ~pd.isnull(data_table['Value'])),  # noqa
            data_table['UID'] >= 7e5
        )
        for k in data_table:
            data_table[k] = data_table[k][mask]

        # save data to csv
        df_info = pd.DataFrame(patient_info)
        df_data = pd.DataFrame(data_table)
        # delete duplicated diagnosis which have the same timestamp
        df_data = df_data[df_data['UID'] < 7e5].append(
            df_data[df_data['UID'] > 7e5].drop_duplicates(keep='first'))
        save_dir_info = 'outputs/info/'
        save_dir_data = 'outputs/data/'

        save_csv(save_dir_info+str(pid)+'.csv', df_info)
        save_csv(save_dir_data+str(pid)+'.csv', df_data)
