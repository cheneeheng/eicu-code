import csv
import json
import os
from tqdm import tqdm

# pulmonary|respiratory failure|Tracheostomy performed during this admission for ventilatory support  # noqa
CHECKED_V_CODES = ['V08', 'V62.84', 'V42.7']
INVALID_CODES = ['31.1']


def separate_icd9_icd10_codes(icd_codes: list):
    """Separate the code into icd9 and icd10.

    Args:
        icd_codes (list): list of icd codes in string.

    Returns:
        icd9: list of valid icd9 codes
        icd10: list of valid icd10 codes
    """
    icd9, icd10 = [], []
    icd_codes = [ic.replace(' ', '') for ic in icd_codes]
    for x in icd_codes:
        # Invalid codes
        if x in INVALID_CODES:
            print(f'Skip invalid code : {x}')
        # Valid codes
        else:
            # ICD 9
            if x[0].isnumeric():
                if len(x.split('.')[0]) != 3:
                    print(f"{x} is not of length 3")
                icd9.append(x)
            # ICD 10
            else:
                if x[0] in ['e', 'E']:
                    if len(x.split('.')[0]) == 4:
                        icd9.append(x)
                    elif len(x.split('.')[0]) == 3:
                        icd10.append(x)
                    else:
                        raise ValueError(f"{x} is not of length 3 or 4")
                elif x[0] in ['v', 'V']:
                    if x in CHECKED_V_CODES:
                        icd10.append(x)
                    else:
                        raise ValueError(f"Please check the {x} code")
                else:
                    icd10.append(x)

    return icd9, icd10


def structure_icd_codes_for_csv(icd_list: list):
    max_len_icd = max([len(i) for i in icd_list])
    icd_list_writeout = []
    for icd_codes in icd_list:
        i = icd_codes
        while len(i) != max_len_icd:
            i += ['']
        icd_list_writeout += [i]
    return icd_list_writeout


if __name__ == "__main__":

    # os.remove("data/resource/raw_icd.csv")
    # with open("data/resource/raw_icd.csv", "a") as f:
    #     pbar = tqdm(os.listdir("outputs/all"))
    #     for i in pbar:
    #         jd = json.load(open("outputs/all" + "/" + i, 'r'))
    #         for ii in jd['diagnosis']['icd9code']:
    #             if ii != "":
    #                 f.write(ii)
    #                 f.write('\n')

    with open('data/resource/raw_icd.csv', 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        icd9_list, icd10_list = [], []
        for row in csvreader:
            icd9, icd10 = separate_icd9_icd10_codes(row)
            icd9_list += icd9
            icd10_list += icd10
        # icd9_list_writeout = structure_icd_codes_for_csv(icd9_list)
        # icd10_list_writeout = structure_icd_codes_for_csv(icd10_list)
        icd9_list = sorted(set(icd9_list))
        icd10_list = sorted(set(icd10_list))

    with open('data/resource/icd9.csv', 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in icd9_list:
            csvwriter.writerow([i])

    with open('data/resource/icd10.csv', 'w+', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in icd10_list:
            csvwriter.writerow([i])
