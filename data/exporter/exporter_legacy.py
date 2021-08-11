""" Legacy code

The functions listed here are NOT USED.

"""

# def get_single_chunked_dataframe(output_folder):

#     query_schema, conn = connect_to_database()

#     query = query_schema + """
#     select *
#     from {}
#     """.format(output_folder.split('/')[-1])

#     df_chunk_iter = pd.read_sql_query(query, conn, chunksize=1)

#     for idx, df_chunk in enumerate(df_chunk_iter):

#         patientunitstayid = df_chunk['patientunitstayid'].tolist()[0]
#         csv_path = f"{output_folder}/{patientunitstayid}.csv"

#         if os.path.exists(csv_path):
#             df_chunk.to_csv(csv_path, mode='a', header=False)
#         else:
#             df_chunk.to_csv(csv_path)

#         if idx % 1000 == 0:
#             print(f"{datetime.datetime.now()} | \
#                   {len(os.listdir(output_folder))}")

#     conn.close()


# def get_multiple_data_and_save_with_cursor(output_folder,
#                                            patientunitstayid_list=[],
#                                            pid=0):
#     """
#     Iterates over `patientunitstayid` and saves entries from all tables
#     with the similar id into json.
#     """

#     query_schema, conn = connect_to_database()
#     cur = conn.cursor()

#     now = time.time()
#     pbar = tqdm(patientunitstayid_list, position=pid+1)
#     for patientunitstayid in pbar:

#         time.sleep(1)
#         pbar.set_description(
#             f"Processing {patientunitstayid}")

#         json_dict = {}

#         for table_name in TABLE_LIST:

#             query = query_schema + """
#             select *
#             from {}
#             where patientunitstayid = {}
#             """.format(table_name, patientunitstayid)
#             cur.execute(query)
#             rows = cur.fetchall()
#             label = [desc[0] for desc in cur.description]

#             if len(rows) == 0:
#                 json_dict[table_name] = {}
#                 for idx, label_i in enumerate(label):
#                     json_dict[table_name][label_i] = []

#             else:
#                 assert len(label) == len(rows[0])
#                 json_dict[table_name] = {}
#                 for idx, label_i in enumerate(label):
#                     col = [r[idx] for r in rows]
#                     col = [float(c)
#                            if isinstance(c, Decimal) else c
#                            for c in col]
#                     json_dict[table_name][label_i] = col

#         json_path = f"{output_folder}/{patientunitstayid}.json"
#         with open(json_path, 'w') as json_file:
#             json.dump(json_dict, json_file)

#     print("Total Time:", time.time()-now)
#     print('-'*80)

#     conn.close()


# def get_multiple_data_and_save(output_folder,
#                                patientunitstayid_list=[],
#                                pid=0):
#     """
#     Iterates over `patientunitstayid` and saves entries from all tables
#     with the similar id into json.
#     """

#     query_schema, conn = connect_to_database()

#     pbar = tqdm(patientunitstayid_list, position=pid+1)
#     for patientunitstayid in pbar:

#         time.sleep(1)
#         pbar.set_description(f"Processing {patientunitstayid}")

#         subset_path = f"{EXPORTER_SUBSET_FOLDER}/{patientunitstayid}.json"
#         with open(subset_path, 'r') as json_file:
#             json_dict_subset = json.load(json_file)

#         json_dict = {}

#         for table_name in TABLE_LIST:

#             if table_name not in TABLE_LIST_SUBSET:

#                 query = query_schema + """
#                 select *
#                 from {}
#                 where patientunitstayid = {}
#                 """.format(table_name, patientunitstayid)
#                 df = pd.read_sql_query(query, conn)

#                 label = df.columns.to_list()

#                 json_dict[table_name] = {}
#                 for label_i in label:
#                     json_dict[table_name][label_i] = df[label_i].tolist()

#             else:
#                 json_dict[table_name] = json_dict_subset[table_name]

#         json_path = f"{output_folder}/{patientunitstayid}.json"
#         with open(json_path, 'w') as json_file:
#             json.dump(json_dict, json_file)

#     conn.close()
