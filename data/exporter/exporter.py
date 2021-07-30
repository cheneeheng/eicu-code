# Import libraries
import pandas as pd
import psycopg2
import getpass
import time
import datetime
import json
import math
from tqdm import tqdm
from multiprocessing import Pool, RLock
import pandas as pd
from decimal import Decimal

# for configuring conection
from configobj import ConfigObj
import os

from data.common import *


def connect_to_database():

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

    print("Getting patient data")

    query_schema, conn = connect_to_database()
    query = query_schema + """
    select *
    from patient
    where unitType in {}
    """.format(UNIT_TYPES)
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

        subset_path = f"{EXPORTER_SUBSET_FOLDER}/{patientunitstayid}.json"
        with open(subset_path, 'r') as json_file:
            json_dict_subset = json.load(json_file)

        json_dict = {}

        for table_name in TABLE_LIST:

            if table_name not in TABLE_LIST_SUBSET:

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

            else:
                json_dict[table_name] = json_dict_subset[table_name]

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
    # get_multiple_data_and_save(output_folder, patientunitstayid_list, 0)

    for i in range(START, CHUNKS, 1):

        def npi(x):
            return math.ceil(len(x) / CHUNKS)

        list_i = patientunitstayid_list[i*npi(patientunitstayid_list):
                                        (i+1)*npi(patientunitstayid_list)]

        output_folder = os.path.join(EXPORTER_FOLDER, f'{i}')
        os.makedirs(output_folder, exist_ok=True)
        parallel_processing(get_multiple_data_and_save, output_folder, list_i)
