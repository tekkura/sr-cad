import csv
import math
import sys
from typing import Any
import numpy as np

import pandas as pd
from pathlib import Path

from pandas import DataFrame, Series
from pandas.io.parsers import TextFileReader

raw: DataFrame = pd.read_csv("toBuy_OctoPart.csv", skiprows=0)
raw = raw.drop(0)
usefulData: DataFrame = raw[['Schematic Reference', 'Qty', 'Manufacturer', 'MPN', 'Distributor [Lowest Price (Selected)]']]

usefulData['Qty'] = usefulData['Qty'].astype(int)
usefulData['Attrition %'] = 10
usefulData['TotalPartsMouser'] = np.ceil(usefulData['Qty'] * 1.1).astype(int)

# Mouser
mouser: DataFrame = usefulData.loc[usefulData['Distributor [Lowest Price (Selected)]'] == "Mouser"]
digikey: DataFrame = usefulData.loc[usefulData['Distributor [Lowest Price (Selected)]'] == "Digi-Key"]

mouser = mouser.drop('Distributor [Lowest Price (Selected)]', axis=1)
digikey = digikey.drop('Distributor [Lowest Price (Selected)]', axis=1)

mouser.to_csv("mouser.csv", index = False)
digikey.to_csv("digikey.csv", index = False)



