# Import libraries
import pandas as pd
import time
import json
import math
from tqdm import tqdm
from multiprocessing import Pool, RLock
import pandas as pd

# import sys
# from pathlib import Path
# sys.path[0] = str(Path(sys.path[0]).parent)

from data_exporter.exporter import connect_to_database, get_patient_list

OUTPUT_FOLDER = f'outputs/210612'
INTERVAL = 436

NUM_PROCESSES = 60

NUM_PATIENTS = 200859
UNIT_TYPES = "('CCU-CTICU','Cardiac ICU','CSICU','CTICU')"
TABLE_LIST = [
    'patient',  # ok
    'treatment',  # ok
    'vitalperiodic',  # ok
    'vitalaperiodic',  # ok
    'nursecharting',  # Very slow, maybe due to large amount of data?
    'lab',  # ok
    'infusiondrug',  # ok
    'intakeoutput',  # Relatively slow, maybe due to large amount of data?
    'diagnosis',  # ok
    'apachepatientresult',  # ok
    'nurseassessment',  # Very slow, maybe due to large amount of data?
    'physicalexam',  # Very slow, maybe due to large amount of data?
    'respiratorycare',  # ok
    'respiratorycharting'  # Very slow, maybe due to large amount of data?
]


def validate_data(output_folder, patientunitstayid):

    query_schema, conn = connect_to_database()

    for table_name in TABLE_LIST:

        query = query_schema + """
        select *
        from {}
        where patientunitstayid = {}
        """.format(table_name, patientunitstayid)
        df = pd.read_sql_query(query, conn)

        json_path = f"{output_folder}/{patientunitstayid}.json"
        with open(json_path, 'r') as json_file:
            json_dict = json.load(json_file)
        df_json = pd.DataFrame(json_dict[table_name])

        if df.equals(df_json):
            print(f"{patientunitstayid}: Table {table_name} is equal.")
        else:
            if df.empty and df_json.empty:
                if all(df.columns == df_json.columns):
                    print(f"{patientunitstayid}: Table {table_name} is equal and empty.")
                else:
                    print(f"{patientunitstayid}: Table {table_name} is not equal and empty.")
            else:
                print(f"{patientunitstayid}: Table {table_name} is not equal.")

    conn.close()


def parallel_processing(func,
                        output_folder,
                        patientunitstayid_list=[]):

    if len(patientunitstayid_list) > NUM_PROCESSES:

        for idx in range(0, len(patientunitstayid_list), NUM_PROCESSES):
            parallel_processing(func,
                                output_folder,
                                patientunitstayid_list[idx*NUM_PROCESSES:
                                                       (idx+1)*NUM_PROCESSES]
                                )

    else:
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


if __name__ == "__main__":

    print('-'*80)

    # 0. patient data from the icu list.
    patientunitstayid_list = get_patient_list()

    # X. validate data from the patient list.
    # for idx in range(0, len(patientunitstayid_list), interval):
    #     validate_data(output_folder, patientunitstayid_list[idx])
    patientunitstayid_list = [
        patientunitstayid_list[idx]
        for idx in range(0, len(patientunitstayid_list), INTERVAL)
    ]
    parallel_processing(validate_data, OUTPUT_FOLDER, patientunitstayid_list)
