"""Validates the exported json files with data from SQL database. """

import json
import os
import pandas as pd

from multiprocessing import Pool, RLock
from tqdm import tqdm

from projects.data_cleaning import *


def validate_data(output_folder, patientunitstayid):

    query_schema, conn = connect_to_database()

    for table_name in TABLE_LIST:

        query = query_schema + """
        select *
        from {}
        where patientunitstayid = {}
        """.format(table_name, patientunitstayid)
        df = pd.read_sql_query(query, conn)
        df.sort_values(df.columns[0], ascending=True,
                       inplace=True, ignore_index=True)

        json_path = f"{output_folder}/{patientunitstayid}.json"
        with open(json_path, 'r') as json_file:
            json_dict = json.load(json_file)
        df_json = pd.DataFrame(json_dict[table_name])
        df_json.sort_values(df_json.columns[0], ascending=True,
                            inplace=True, ignore_index=True)

        if df.equals(df_json):
            print(f"{patientunitstayid}: Table {table_name} is equal.")
        else:
            if df.empty and df_json.empty:
                print(f"{patientunitstayid}: Table {table_name} is empty")

                if all(df.columns == df_json.columns):
                    print(f"{patientunitstayid}: -- Labels are equal.")
                else:
                    raise ValueError(
                        f"{patientunitstayid}: -- Labels are not equal.")
            else:
                raise ValueError(
                    f"{patientunitstayid}: Table {table_name} is not equal.")

    conn.close()


def parallel_processing(func,
                        output_folder,
                        patientunitstayid_list=[]):

    if len(patientunitstayid_list) == 0:
        pass

    elif len(patientunitstayid_list) <= NUM_PROCESSES:
        np = len(patientunitstayid_list)
        a0 = output_folder
        a1 = patientunitstayid_list
        argument_list = [(a0, a1[pid]) for pid in range(np)]

        pool = Pool(processes=np,
                    initargs=(RLock(),),
                    initializer=tqdm.set_lock)
        jobs = [pool.apply_async(func, args=arg) for arg in argument_list]
        pool.close()
        result_list = [job.get() for job in jobs]

    else:
        for idx in range(0, len(patientunitstayid_list), NUM_PROCESSES):
            parallel_processing(func,
                                output_folder,
                                patientunitstayid_list[idx*NUM_PROCESSES:
                                                       (idx+1)*NUM_PROCESSES]
                                )


if __name__ == "__main__":

    print('-'*80)

    # 0. patient data from the icu list.
    patientunitstayid_list = get_patient_list()

    if len(patientunitstayid_list) != len(os.listdir(VALIDATE_FOLDER)):
        raise ValueError(f"Number of data entries is incorrect. \
                           #Patients : {len(patientunitstayid_list)} != \
                           #Files : {len(os.listdir(VALIDATE_FOLDER))}")

    # X. validate data from the patient list.
    # for idx in range(0, len(patientunitstayid_list), interval):
    #     validate_data(output_folder, patientunitstayid_list[idx])
    patientunitstayid_list = [
        patientunitstayid_list[idx]
        for idx in range(0, len(patientunitstayid_list), VALIDATE_INTERVAL)
    ]
    parallel_processing(validate_data, VALIDATE_FOLDER, patientunitstayid_list)

    print("="*80)
    print(f"Successfully validated {len(patientunitstayid_list)} entries.")
    print("="*80)
