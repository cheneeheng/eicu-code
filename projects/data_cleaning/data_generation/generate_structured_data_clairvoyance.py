"""
Convert the structured data into claivoyance format.
"""

import os
import numpy as np
import pandas as pd

from projects.data_cleaning import *


if __name__ == "__main__":
    dir_info = os.path.join(DATA_CLEANING_OUTPUT_FOLDER, 'info')
    dir_data = os.path.join(DATA_CLEANING_OUTPUT_FOLDER, 'data')
