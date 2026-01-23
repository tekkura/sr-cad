# See https://gitlab.com/kicad/code/kicad/-/blob/master/pcbnew/footprint.h#L70 for enum definitions

import pcbnew
import sys
from enum import Enum

board = pcbnew.LoadBoard(sys.argv[1])
footprints = board.GetFootprints()

class FOOTPRINT_ATTR_T(Enum):
    FP_THROUGH_HOLE             = 0x0001
    FP_SMD                      = 0x0002
    FP_EXCLUDE_FROM_POS_FILES   = 0x0004
    FP_EXCLUDE_FROM_BOM         = 0x0008
    FP_BOARD_ONLY               = 0x0010  # Footprint has no corresponding symbol
    FP_JUST_ADDED               = 0x0020  # Footprint just added by netlist update
    FP_ALLOW_SOLDERMASK_BRIDGES = 0x0040
    FP_ALLOW_MISSING_COURTYARD  = 0x0080
    FP_DNP                      = 0x0100


for footprint in footprints:
    attr = footprint.GetAttributes()
    if attr & FOOTPRINT_ATTR_T.FP_EXCLUDE_FROM_BOM.value:
        print(footprint.GetReference() + " is excluded from BOM")
    # This doesn't seem to match anything for some reason.
    if attr & FOOTPRINT_ATTR_T.FP_DNP.value:
        print(footprint.GetReference() + " is DNP")
