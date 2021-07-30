import json
import os
import numpy as np
import shutil


# for i in os.listdir("outputs/all/0"):
#     jd1 = json.load(open(f"outputs/all/0/{i}", 'r'))
#     jd2 = json.load(
#         open(f"outputs/json_data/patientsubset_tablesubset/{i}", 'r'))

#     for k in jd1.keys():
#         if k not in jd2:
#             continue
#         else:
#             assert jd1[k] == jd2[k]

#     # if jd1['admissiondrug']['patientunitstayid'] == []:
#     #     continue
#     # if jd1['respiratoryCare']['airwaysize'][0] == '':
#     #     continue

#     assert jd1 != jd2

#     # for i in jd1.keys():
#     #     print(i)
#     #     for ii in jd1[i].keys():
#     #         print(ii)
#     #     print("------")
#     # break

# print("all good")

# BASE_PATH = "outputs/all"

# files = []
# print(len(os.listdir(BASE_PATH)))
# for i in os.listdir(BASE_PATH):
#     for j in os.listdir(BASE_PATH + "/" + i):
#         files.append(j)

# files_unique = np.unique(files)

# assert len(files_unique) == len(files)
# print(len(files))

# BASE_PATH = "outputs/all"
# for fol in os.listdir(BASE_PATH):
#     for fil in os.listdir(BASE_PATH + "/" + fol):
#         shutil.move(BASE_PATH + "/" + fol + "/" + fil,
#                     BASE_PATH)
#         exit

# from collections import Counter
# import os
# import json
# from tqdm import tqdm
# from time import sleep

# entries1, entries2, entries3 = [], {}, {}

# with tqdm(total=len(os.listdir("outputs/all"))) as pbar:
#     for filename in sorted(os.listdir("outputs/all")):
#         data = json.load(open("outputs/all/" + filename))

#         tmp_data = []
#         for i, j, k in zip(data['nurseCharting']['nursingchartcelltypecat'],
#                            data['nurseCharting']['nursingchartcelltypevallabel'],
#                            data['nurseCharting']['nursingchartcelltypevalname']):
#             tmp_data.append(i + '___' + j + '___' + k)

#         entries1 += tmp_data

#         # for i, j in zip(tmp_data, data['nurseCharting']['nursingchartcelltypecat']):
#         #     if i not in entries2:
#         #         entries2[i] = j
#         #     else:
#         #         assert entries2[i] == j, f"{i}, {entries2[i]}, {j}"
#         sleep(0.001)
#         pbar.update(1)

# entries = {k: v for k, v in sorted(
#     Counter(entries1).items(), key=lambda item: item[1], reverse=True)}

# for k in entries.keys():
#     print(k.split('___')[0])
# print("---------------------------------------------------")
# for k in entries.keys():
#     print(k.split('___')[1])
# print("---------------------------------------------------")
# for k in entries.keys():
#     print(k.split('___')[2])
# print("---------------------------------------------------")
# for v in entries.values():
#     print(v)


#     print(entries2[k])
# print("---------------------------------------------------")
# for k in entries:
#     print(entries3[k])


# with open('outputs/infusiondrug_count.txt', 'a') as file:
#     for k in entries:
#         file.write(f'{k}: {entries[k]}\n')

# import csv

# with open('outputs/infusion.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         if row['Entry Name'][-1] == ')':
#             unit = row['Entry Name'].split('(')[-1]
#             if "Unknown" in unit:
#                 print('')
#             else:
#                 print(unit[:-1])
#         else:
#             print('')


# with open('outputs/tmp.txt', 'w') as file:

#     BASE_PATH = "outputs/all"
#     for fil in os.listdir(BASE_PATH):
#         json_file = os.path.join(BASE_PATH, fil)
#         with open(json_file, 'r') as jf:
#             json_dict = json.load(jf)

#         tab = json_dict['infusionDrug']

#         for i in range(len(tab['drugname'])):
#             if 'Amiodarone' in tab['drugname'][i] or 'amiodarone' in tab['drugname'][i]:
#                 file.write(
#                     f"{tab['drugname'][i]} : {tab['drugrate'][i]} : {tab['infusionrate'][i]} : {tab['drugamount'][i]} : {tab['volumeoffluid'][i]}: \n")

#             pass

#         pass

cil = open("outputs/custominfusionlist.txt", 'r')

Lines = cil.readlines()
print(len(Lines))
