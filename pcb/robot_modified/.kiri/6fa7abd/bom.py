# Import the KiCad python helper module and the csv formatter
import math

import kicad_netlist_reader
import csv
import sys
from pathlib import Path

# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])

batch = 5

try:
    bomFile = open(str(Path('robot_bom.csv')), 'w')
    toBuy = open(str(Path('DNPtoBuy.csv')), 'w')
    nextPCB = open(str(Path('nextPCB.csv')), 'w')
    pcbway = open(str(Path('pcbway.csv')), 'w')
    sierra = open(str(Path('sierra.csv')), 'w')
    jlc = open(str(Path('jlc.csv')), 'w')
except IOError:
    e = "Can't open output file for writing: "
    print(__file__, ":", e, sys.stderr)
    f = sys.stdout

# Create a new csv writer object to use as the output formatter
out_bomFile = csv.writer(bomFile, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
out_toBuy = csv.writer(toBuy, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
out_nextPCB = csv.writer(nextPCB, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
out_pcbway = csv.writer(pcbway, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
out_sierra = csv.writer(sierra, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
out_jlc = csv.writer(jlc, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)

# out_bomFile.writerow(['Ref', 'Qty Single Board', 'Batch Size', 'Qty Total Batch', 'Stock', 'Need to Buy', 'Value', 'Manufacturer', 'Part Number', 'Description', 'Footprint', 'Type'])
out_bomFile.writerow([
                    'Manufacturer', 
                    'Part Number',
                    'Ref',
                    'Qty Single Board', 
                    'Description', 
                    'Batch Size',
                    'Qty Total Batch', 
                    'Customer Stock', 
                    #'Need to Buy', 
                    'Value', 
                    'Footprint'])
out_toBuy.writerow([
                    'Manufacturer', 
                    'Part Number',
                    'Ref',
                    'Qty Single Board', 
                    'Description', 
                    'Batch Size',
                    'Qty Total Batch', 
                    'Stock', 
                    'Need to Buy', 
                    'Value', 
                    'Footprint'])
out_nextPCB.writerow(['Part Index',
                    'Manufacturer Part Number',
                    'Qty', 
                    'Designator',
                    'Customer Supply', 
                    'Customer Remark', 
                    'Manufacturer'])
out_pcbway.writerow(['Item #',
                    'Designator',
                    'Qty', 
                    'Manufacturer',
                    'Mfg Part #',
                    'Description / Value',
                    'Package/Footprint',
                     'Type',
                    'Your Instruction / Notes', 
                    'Customer Supply', 
                    ])
out_sierra.writerow(['Item #',
                    'Qty', 
                    'Mfg Part #',
                    'Do Not Install',
                    'Designator',
                    'Vendor',
                    'Vendor Part Number',
                    'Value',
                    'Size / Footprint',
                    'Part description/specs',
                    'Manufacturer',
                    'Customer Supply', 
                    ])
out_jlc.writerow([
                    'Comment', 
                    'Designator',
                    'Footprint',
                    'JLCPCB Part #（optional)'
                    ])

# Get all of the components in groups of matching parts + values
# (see ky_generic_netlist_reader.py)
grouped = net.groupComponents()
part_idx: int = 1

# Output all of the component information
for group in grouped:
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        refs += component.getRef() + ","
        quantity = len(group)
        totalQty = quantity * batch
        try:
            stock = int(component.getField("Stock"))
            print("Stock: " + str(stock) + " for " + component.getField("Part Number"))
        except:
            stock = 0

        toBuyCnt = totalQty - stock
        if toBuyCnt < 0:
            toBuyCnt = 0

    refs = refs.removesuffix(",")

    if component.getExcludeFromBOM():
        print("Excluding " + component.getRef() + " from BOM")
    if component.getExcludeFromBoard():
        print("Excluding " + component.getRef() + " from Board")


    # BOM excluding DNP parts 
    if not component.getDNP():
        out_bomFile.writerow([component.getField("Manufacturer"),
            component.getField("Part Number"),
            refs,
            quantity,
            component.getDescription(),
            batch,
            totalQty,
            stock,
            #toBuyCnt,
            component.getValue(),
            component.getFootprint()])

        out_nextPCB.writerow([
            part_idx,
            component.getField("Part Number"),
            quantity,
            refs,
            0,
            component.getDescription(),
            component.getField("Manufacturer")
            ])
        out_pcbway.writerow([
            part_idx,
            refs,
            quantity,
            component.getField("Manufacturer"),
            component.getField("Part Number"),
            component.getDescription(),
            component.getFootprint(),
            component.getField("Type"),
            component.getDescription(),
            stock
            ])
        out_sierra.writerow([
            part_idx,
            quantity,
            component.getField("Part Number"),
            component.getDNP(),
            refs,
            '',
            '',
            component.getValue(),
            component.getFootprint(),
            component.getDescription(),
            component.getField("Manufacturer"),
            stock
            ])
        out_jlc.writerow([
            component.getDescription(),
            refs,
            component.getFootprint(),
            component.getField("Part Number"),
            ])
        part_idx=part_idx+1

    # DNP Self Populating Parts to Buy on my own
    else:
        if toBuyCnt > 0:
            out_toBuy.writerow([component.getField("Manufacturer"),
                component.getField("Part Number"),
                refs,
                quantity,
                component.getDescription(),
                batch,
                totalQty,
                stock,
                toBuyCnt,
                component.getValue(),
                component.getFootprint()])
