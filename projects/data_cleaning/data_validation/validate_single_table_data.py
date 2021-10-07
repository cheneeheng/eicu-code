"""
Validates the exported json files with data from
a single table in SQL database.
"""

import json
import os

from projects.data_cleaning import *


def testing():
    """Testing. """

    for fil in sorted(os.listdir(VALIDATE_FOLDER)):
        json_file = os.path.join(VALIDATE_FOLDER, fil)
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

    data_list = []

    with open('outputs/inspection_infusion.txt', 'w') as file:

        counter = 0

        for file in sorted(os.listdir(VALIDATE_FOLDER)):
            json_file = os.path.join(VALIDATE_FOLDER, file)
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
