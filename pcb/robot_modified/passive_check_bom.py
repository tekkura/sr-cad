# Import the KiCad python helper module and the csv formatter
import math
import re

import kicad_netlist_reader
import csv
import sys
from pathlib import Path

# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])

try:
    bomFile = open(str(Path('passives_bom.csv')), 'w')
except IOError:
    e = "Can't open output file for writing: "
    print(__file__, ":", e, sys.stderr)
    f = sys.stdout

# Create a new csv writer object to use as the output formatter
out_bomFile = csv.writer(bomFile, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)

# out_bomFile.writerow(['Ref', 'Qty Single Board', 'Batch Size', 'Qty Total Batch', 'Stock', 'Need to Buy', 'Value', 'Manufacturer', 'Part Number', 'Description', 'Footprint', 'Type'])
out_bomFile.writerow([
                    'Ref',
                    'Footprint',
                    'Manufacturer', 
                    'Part Number',
                    ])

# Get all of the components in groups of matching parts + values
# (see ky_generic_netlist_reader.py)
grouped = net.groupComponents()
part_idx: int = 1
pattern = r'^[CR](\d+)'

# Output all of the component information
for group in grouped:
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:

        refs += component.getRef() + ";"

    refs = refs.removesuffix(",")

    # Check if the component is a resistor or capacitor
    if re.search(pattern, refs):
        out_bomFile.writerow([
            refs,
            component.getFootprint(),
            component.getField("Manufacturer"),
            component.getField("Part Number")
            ])
    else:
        print("Not a resistor or capacitor: " + refs)
