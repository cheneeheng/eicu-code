# Import libraries
import os
from typing import Counter
import pandas as pd
import json
from tqdm import tqdm
from multiprocessing import Pool, RLock
import pandas as pd
from time import sleep


BASE_PATH = "outputs/all"


def testing():
    """Testing. """

    for fil in sorted(os.listdir(BASE_PATH)):
        json_file = os.path.join(BASE_PATH, fil)
        with open(json_file, 'r') as jf:
            json_dict = json.load(jf)

        tab = json_dict['infusionDrug']

        for i in range(len(tab['drugname'])):
            if "Norepinephrine (mcg/kg/min)" in tab['drugname'][i]:
                print(
                    f"{tab['drugname'][i]}:" +
                    f"{tab['drugrate'][i]}:" +
                    f"{tab['infusionrate'][i]}:" +
                    f"{tab['drugamount'][i]}:" +
                    f"{tab['volumeoffluid'][i]}\n")


def validate_infusion():
    """Exports data for manual inspection. """

    with open("data/validation/validate_infusion_list", 'r') as data_list_file:
        data_list = data_list_file.readlines()
        data_list = [i.replace('\n', '') for i in data_list]

    with open('outputs/inspection_infusion.txt', 'w') as file:

        counter = 0

        for fil in sorted(os.listdir(BASE_PATH)):
            json_file = os.path.join(BASE_PATH, fil)
            with open(json_file, 'r') as jf:
                json_dict = json.load(jf)

            tab = json_dict['infusionDrug']

            for i in range(len(tab['drugname'])):
                if tab['drugname'][i] in data_list:
                    file.write(
                        f"{tab['drugname'][i]}:" +
                        f"{tab['drugrate'][i]}:" +
                        f"{tab['infusionrate'][i]}:" +
                        f"{tab['drugamount'][i]}:" +
                        f"{tab['volumeoffluid'][i]}\n")

            counter += 1
            print(counter)


if __name__ == "__main__":

    # validate_infusion()
    testing()
