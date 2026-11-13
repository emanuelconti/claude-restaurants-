"""
Read the daily date block out of a Business Objects .xls export.

Layout (verified on real exports, both metals):

    row 1 (0-indexed): header  -> "Date d'effet Poste de commande.", "Tonnes", "Tonnes Cu"/"Tonnes Al"
    row 2..N-1:        one posting day per row
    row N:              "Total" row -- must be ignored

Column A of the BO sheet is blank; the real columns are B (date), C (cable
tonnes), D (metal tonnes). We key off the date column's cell type rather than
the "Total" label because the label cell is sometimes text ("Total") and
sometimes blank, depending on export -- but a genuine posting day always has
an Excel date in column B, so "column B is a valid date" is the one detection
rule that works for both metals.

Office Scripts port note: the equivalent there is reading the same exported
range and filtering rows where the date cell parses -- no special-casing of
the trailing Total row needed beyond that same rule.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List

import xlrd

BO_DATE_COL = 1     # column B (0-indexed)
BO_TONNES_COL = 2   # column C (0-indexed)
BO_METAL_COL = 3    # column D (0-indexed)


@dataclass(frozen=True)
class BoRow:
    posting_date: date
    tonnes_cable: float
    tonnes_metal: float


def read_bo_daily_rows(bo_path: str, sheet_name: str) -> List[BoRow]:
    """Read and return the daily posting rows, sorted by date, Total row excluded."""
    wb = xlrd.open_workbook(bo_path, formatting_info=False)
    sheet = wb.sheet_by_name(sheet_name)

    rows: List[BoRow] = []
    for r in range(sheet.nrows):
        date_cell = sheet.cell(r, BO_DATE_COL)
        if date_cell.ctype != xlrd.XL_CELL_DATE:
            continue  # header, blank spacer row, or the trailing "Total" row
        posting_dt = xlrd.xldate_as_datetime(date_cell.value, wb.datemode)
        tonnes_cable = sheet.cell(r, BO_TONNES_COL).value or 0.0
        tonnes_metal = sheet.cell(r, BO_METAL_COL).value or 0.0
        rows.append(BoRow(posting_dt.date(), float(tonnes_cable), float(tonnes_metal)))

    rows.sort(key=lambda row: row.posting_date)
    return rows
