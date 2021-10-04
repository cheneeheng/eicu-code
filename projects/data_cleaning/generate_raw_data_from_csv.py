"""Exports data from SQL database into json files. """

import csv
import datetime
import getpass
import json
import math
import os
import pandas as pd
import psycopg2
import time

from configobj import ConfigObj
from decimal import Decimal
from multiprocessing import Pool, RLock
from tqdm import tqdm

from projects.data_cleaning import *


MAPPING = {i: j for i, j in zip(CSV_FILE_LIST, TABLE_LIST)}


def get_patient_list():
    """Get the list of patientid based on `UNIT_TYPES` ."""

    df = pd.read_csv(RAW_CSV_FOLDER + '/patient.csv')
    df = df[df['unittype'].isin(UNIT_TYPES)]
    df.sort_values('patientunitstayid', ascending=True, inplace=True)
    patientunitstayid_list = df['patientunitstayid'].tolist()

    print(f"Number of patient data entries:", df.shape[0])

    return patientunitstayid_list


def get_data_and_save(output_folder,
                      csv_filename,
                      patientunitstayid_list=[],
                      pid=0):
    """
    Iterates over `patientunitstayid` and saves entries from all tables
    with the similar id into json.
    """
    chunksize = 10 ** 6
    df_part = pd.read_csv(RAW_CSV_FOLDER + f'/{csv_filename}.csv',
                          nrows=chunksize)

    c = 1
    pbar = tqdm(patientunitstayid_list, position=pid+1)
    for patientunitstayid in pbar:

        time.sleep(1)
        pbar.set_description(f"Processing {patientunitstayid}")

        json_path = f"{output_folder}/{patientunitstayid}.json"

        if os.path.isfile(json_path):
            with open(json_path, 'r') as jf:
                json_dict = json.load(jf)
        else:
            json_dict = {}

        df = df_part[df_part['patientunitstayid'] == patientunitstayid]
        while len(df) == 0 and len(df_part) != 0:
            df_part = pd.read_csv(RAW_CSV_FOLDER + f'/{csv_filename}.csv',
                                  skiprows=range(1, chunksize*c+1),
                                  nrows=chunksize)
            df = df_part[df_part['patientunitstayid'] == patientunitstayid]
            c += 1
        label = df.columns.to_list()

        json_dict[MAPPING[csv_filename]] = {}
        for label_i in label:
            json_dict[MAPPING[csv_filename]][label_i] = df[label_i].tolist()

        with open(json_path, 'w') as json_file:
            json.dump(json_dict, json_file)


# def get_data_and_save(output_folder,
#                       csv_filename,
#                       patientunitstayid_list=[],
#                       pid=0):
#     """
#     Iterates over `patientunitstayid` and saves entries from all tables
#     with the similar id into json.
#     """
#     df_main = pd.read_csv(RAW_CSV_FOLDER + f'/{csv_filename}.csv')

#     pbar = tqdm(patientunitstayid_list, position=pid+1)
#     for patientunitstayid in pbar:

#         time.sleep(1)
#         pbar.set_description(f"Processing {patientunitstayid}")

#         json_path = f"{output_folder}/{patientunitstayid}.json"

#         if os.path.isfile(json_path):
#             with open(json_path, 'r') as jf:
#                 json_dict = json.load(jf)
#         else:
#             json_dict = {}

#         df = df_main[df_main['patientunitstayid'] == patientunitstayid]
#         label = df.columns.to_list()

#         json_dict[MAPPING[csv_filename]] = {}
#         for label_i in label:
#             json_dict[MAPPING[csv_filename]][label_i] = df[label_i].tolist()

#         with open(json_path, 'w') as json_file:
#             json.dump(json_dict, json_file)


def parallel_processing(func,
                        csv_filename,
                        output_folder,
                        patientunitstayid_list=[]):

    def npi(x):
        return math.ceil(len(x) / NUM_PROCESSES)

    num_id_per_process = npi(patientunitstayid_list)

    argument_list = [
        (output_folder,
         csv_filename,
         patientunitstayid_list[pid*num_id_per_process:
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


if __name__ == "__main__":

    print('-'*80)

    # 0. patient data from the icu list.
    patientunitstayid_list = get_patient_list()
    patientunitstayid_list = patientunitstayid_list[:3]
    print('-'*80)

    # 1. data from the patient list.
    def npi(x):
        return math.ceil(len(x) / CHUNKS)

    interval = 1

    for csv_filename in CSV_FILE_LIST:
        print("Processing :", csv_filename)

        for i in range(START, CHUNKS, interval):

            x = npi(patientunitstayid_list) * i
            y = npi(patientunitstayid_list) * (i + interval)
            list_i = patientunitstayid_list[x:y]

            output_folder = os.path.join(EXPORTER_FOLDER, f'{i}')
            os.makedirs(output_folder, exist_ok=True)
            parallel_processing(get_data_and_save,
                                csv_filename, output_folder, list_i)
