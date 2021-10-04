"""Exports data from SQL database into json files. """

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


def connect_to_database():
    """Connect to the SQL database. """

    # Create a database connection using settings from config file
    config = 'db/config.ini'

    # connection info
    conn_info = dict()
    if os.path.isfile(config):
        config = ConfigObj(config)
        conn_info["sqluser"] = config['username']
        conn_info["sqlpass"] = config['password']
        conn_info["sqlhost"] = config['host']
        conn_info["sqlport"] = config['port']
        conn_info["dbname"] = config['dbname']
        conn_info["schema_name"] = config['schema_name']
    else:
        conn_info["sqluser"] = 'postgres'
        conn_info["sqlpass"] = ''
        conn_info["sqlhost"] = 'localhost'
        conn_info["sqlport"] = 5432
        conn_info["dbname"] = 'eicu'
        conn_info["schema_name"] = 'public,eicu_crd'

    # Connect to the eICU database
    print('Database: {}'.format(conn_info['dbname']))
    print('Username: {}'.format(conn_info["sqluser"]))

    if conn_info["sqlpass"] == '':
        # try connecting without password, i.e. peer or OS authentication
        try:
            if ((conn_info["sqlhost"] == 'localhost') &
                (conn_info["sqlport"] == '5432')):  # noqa
                conn = psycopg2.connect(dbname=conn_info["dbname"],
                                        user=conn_info["sqluser"])
            else:
                conn = psycopg2.connect(dbname=conn_info["dbname"],
                                        host=conn_info["sqlhost"],
                                        port=conn_info["sqlport"],
                                        user=conn_info["sqluser"])
        except:  # noqa
            conn_info["sqlpass"] = getpass.getpass('Password: ')

            conn = psycopg2.connect(dbname=conn_info["dbname"],
                                    host=conn_info["sqlhost"],
                                    port=conn_info["sqlport"],
                                    user=conn_info["sqluser"],
                                    password=conn_info["sqlpass"])

    else:
        conn = psycopg2.connect(dbname=conn_info["dbname"],
                                host=conn_info["sqlhost"],
                                port=conn_info["sqlport"],
                                user=conn_info["sqluser"],
                                password=conn_info["sqlpass"])

    query_schema = 'set search_path to ' + conn_info['schema_name'] + ';'

    print(">>>>> Connected to DB <<<<<")

    return query_schema, conn


def get_patient_list():
    """Get the list of patientid based on `UNIT_TYPES_SQL` ."""

    print("Getting patient data")

    query_schema, conn = connect_to_database()
    if UNIT_TYPES_SQL is not None:
        query = query_schema + """
        select *
        from patient
        where unitType in {}
        """.format(UNIT_TYPES_SQL)
    else:
        query = query_schema + """
        select *
        from patient
        """
    df = pd.read_sql_query(query, conn)
    df.sort_values('patientunitstayid', ascending=True, inplace=True)
    conn.close()

    print(f"Number of patient data entries:", df.shape[0])
    print('-'*80)

    patientunitstayid_list = df['patientunitstayid'].tolist()
    return patientunitstayid_list


def get_multiple_data_and_save(output_folder,
                               patientunitstayid_list=[],
                               pid=0):
    """
    Iterates over `patientunitstayid` and saves entries from all tables
    with the similar id into json.
    """

    query_schema, conn = connect_to_database()

    pbar = tqdm(patientunitstayid_list, position=pid+1)
    for patientunitstayid in pbar:

        time.sleep(1)
        pbar.set_description(f"Processing {patientunitstayid}")

        json_dict = {}

        for table_name in TABLE_LIST:

            query = query_schema + """
            select *
            from {}
            where patientunitstayid = {}
            """.format(table_name, patientunitstayid)
            df = pd.read_sql_query(query, conn)

            label = df.columns.to_list()

            json_dict[table_name] = {}
            for label_i in label:
                json_dict[table_name][label_i] = df[label_i].tolist()

        json_path = f"{output_folder}/{patientunitstayid}.json"
        with open(json_path, 'w') as json_file:
            json.dump(json_dict, json_file)

    conn.close()


def parallel_processing(func,
                        output_folder,
                        patientunitstayid_list=[]):

    def npi(x):
        return math.ceil(len(x) / NUM_PROCESSES)

    num_id_per_process = npi(patientunitstayid_list)

    argument_list = [
        (output_folder,
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

    # 1. data from the patient list.
    def npi(x):
        return math.ceil(len(x) / CHUNKS)

    interval = 1

    for i in range(START, CHUNKS, interval):

        x = npi(patientunitstayid_list) * i
        y = npi(patientunitstayid_list) * (i + interval)
        list_i = patientunitstayid_list[x:y]

        output_folder = os.path.join(EXPORTER_FOLDER, f'{i}')
        os.makedirs(output_folder, exist_ok=True)
        parallel_processing(get_multiple_data_and_save, output_folder, list_i)
