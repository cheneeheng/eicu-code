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

BASE_PATH = "outputs/all"

files = []
print(len(os.listdir(BASE_PATH)))
for i in os.listdir(BASE_PATH):
    for j in os.listdir(BASE_PATH + "/" + i):
        files.append(j)

files_unique = np.unique(files)

assert len(files_unique) == len(files)
print(len(files))

# BASE_PATH = "outputs/all"
# for fol in os.listdir(BASE_PATH):
#     for fil in os.listdir(BASE_PATH + "/" + fol):
#         shutil.move(BASE_PATH + "/" + fol + "/" + fil,
#                     BASE_PATH)
#         exit
