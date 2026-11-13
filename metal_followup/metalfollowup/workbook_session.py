"""
All interaction with the monthly .xlsx workbook goes through here, using
LibreOffice's UNO API instead of openpyxl.

Why UNO and not openpyxl: these are real production workbooks with charts,
embedded images, comments and a corporate sensitivity label. A plain
openpyxl load-and-save round-trip silently DROPS the charts, every embedded
image, threaded comments and the sensitivity label metadata (verified while
building this tool -- diff the zip contents of an openpyxl-saved copy against
the original and see for yourself). Driving the same LibreOffice engine that
does the recalculation step to also make the cell edits keeps everything to
a single, minimal-loss round trip instead of two lossy ones.

Office Scripts port note: none of this UNO machinery exists there. In Office
Scripts every method below becomes a few lines using worksheet.getRange(...)
.setValues(...), workbook.application.calculate(...), and
range.getCellProperties(...).errorType -- the *logic* (which cells, which
matching rule, which checks) is what this module is trying to make obvious,
so that translation is mechanical.
"""

import os
import socket
import subprocess
import tempfile
import time
import shutil
from contextlib import closing
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional

import uno
from com.sun.star.beans import PropertyValue

from .bo_import import BoRow
from .config import MetalConfig

EXCEL_EPOCH = date(1899, 12, 30)  # matches the BO export's xlrd datemode=0


def _date_to_excel_serial(d: date) -> int:
    return (d - EXCEL_EPOCH).days


def _find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _make_prop(name, value):
    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


@dataclass
class RowChange:
    row: int
    action: str  # "update" | "append" | "unchanged"
    posting_date: date
    old_tonnes: Optional[float]
    old_metal: Optional[float]
    new_tonnes: float
    new_metal: float


@dataclass
class PriceChange:
    cell: str
    old_price: Optional[float]
    new_price: float
    audit_cell: str
    old_audit: Optional[str]
    new_audit: str


@dataclass
class CellError:
    sheet: str
    cell: str
    error_code: int


@dataclass
class HeaderStatus:
    workday_number: Optional[float]  # "import par date"!B1 -- Nb jours écoulés
    as_of_date_text: str             # "import par date"!D1 -- date the daily figures are "as of"


@dataclass
class SyntheseDailyRow:
    date_text: str
    daily_tonnes: float
    workday: Optional[float]
    actual_cumulative: Optional[float]
    forecast_cumulative: Optional[float]
    gap: Optional[float]


@dataclass
class SyntheseSummary:
    daily_rows: List[SyntheseDailyRow] = field(default_factory=list)
    total_actual: Optional[float] = None
    total_workdays: Optional[float] = None
    total_forecast: Optional[float] = None
    total_gap: Optional[float] = None


class WorkbookSession:
    """One LibreOffice headless session, one document, open for the lifetime
    of a `with` block. Keeps the write -> recalc -> verify -> read -> save
    pipeline inside a single round trip through the file."""

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self._profile_dir = None
        self._proc = None
        self._ctx = None
        self._desktop = None
        self.doc = None

    def __enter__(self):
        self._profile_dir = tempfile.mkdtemp(prefix="metal_followup_lo_")
        port = _find_free_port()

        env = os.environ.copy()
        # The workbook's own date formulas use French TEXT() format codes
        # ("jj/mm/aaaa"). Under the default/English locale those raise
        # #VALUE! -- LibreOffice needs to be told to use French so the
        # existing formulas (which we must not touch) evaluate correctly.
        env["LANG"] = "fr_FR.UTF-8"
        env["LC_ALL"] = "fr_FR.UTF-8"

        self._proc = subprocess.Popen(
            [
                "soffice",
                "--headless",
                "--norestore",
                "--nologo",
                "--nofirststartwizard",
                f"-env:UserInstallation=file://{self._profile_dir}",
                f"--accept=socket,host=localhost,port={port};urp;",
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx
        )
        last_exc = None
        for _ in range(40):
            try:
                self._ctx = resolver.resolve(
                    f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext"
                )
                break
            except Exception as exc:  # noqa: BLE001 - retry loop, real error re-raised below
                last_exc = exc
                time.sleep(0.5)
        else:
            self._cleanup()
            raise RuntimeError(f"Could not connect to LibreOffice: {last_exc}")

        self._desktop = self._ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self._ctx
        )
        url = uno.systemPathToFileUrl(self.path)
        self.doc = self._desktop.loadComponentFromURL(
            url, "_blank", 0, (_make_prop("Hidden", True),)
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.doc is not None:
                self.doc.close(False)
        finally:
            self._cleanup()

    def _cleanup(self):
        if self._proc is not None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=10)
            except Exception:  # noqa: BLE001
                self._proc.kill()
        if self._profile_dir and os.path.isdir(self._profile_dir):
            shutil.rmtree(self._profile_dir, ignore_errors=True)

    # -- helpers -----------------------------------------------------------

    def _sheet(self, name: str):
        return self.doc.Sheets.getByName(name)

    def _cell(self, sheet_name: str, row1: int, col1: int):
        """1-indexed (spreadsheet-style) cell lookup; UNO itself is 0-indexed."""
        return self._sheet(sheet_name).getCellByPosition(col1 - 1, row1 - 1)

    # -- BO import: write A:C only, never touch D ---------------------------

    def apply_bo_rows(self, config: MetalConfig, bo_rows: List[BoRow]) -> List[RowChange]:
        """Match each BO posting day to the monthly sheet by date and update
        it in place; append a new row for any date not yet present.

        A row counts as "a real posting day already on the sheet" only if
        its date cell holds a positive numeric value. This is what lets us
        skip a stray leftover row cleanly: sometimes a previous manual paste
        left the BO export's own "Total" row behind (text "Total", or blank,
        in column A) sitting right after the last real date. Because that
        cell's numeric value is 0, it's never mistaken for a posting day --
        and if a genuinely new date needs to be appended there, we simply
        overwrite that row's A/B/C, which clears the leftover for free.

        This always writes into the in-memory document (which is always a
        throwaway copy -- see WorkbookSession callers in cli.py). Whether
        that ends up persisted to disk is decided later, by --dry-run.
        """
        sheet_name = config.import_sheet
        col_date, col_tonnes, col_metal = (
            config.import_col_date,
            config.import_col_tonnes,
            config.import_col_metal,
        )

        existing_by_date: Dict[date, int] = {}
        last_valid_row = config.import_first_data_row - 1
        row = config.import_first_data_row
        consecutive_blank = 0
        while consecutive_blank < 10:  # generous run-off past the last used row
            date_cell = self._cell(sheet_name, row, col_date)
            tonnes_cell = self._cell(sheet_name, row, col_tonnes)
            metal_cell = self._cell(sheet_name, row, col_metal)
            if date_cell.getValue() > 0:
                serial = int(date_cell.getValue())
                posting = EXCEL_EPOCH + timedelta(days=serial)
                existing_by_date[posting] = row
                last_valid_row = row
                consecutive_blank = 0
            elif (
                date_cell.getString() == ""
                and tonnes_cell.getValue() == 0
                and metal_cell.getValue() == 0
            ):
                consecutive_blank += 1
            else:
                consecutive_blank = 0  # stray leftover row (e.g. old "Total" paste) -- keep scanning
            row += 1

        append_pointer = last_valid_row + 1
        changes: List[RowChange] = []

        for bo_row in bo_rows:
            if bo_row.posting_date in existing_by_date:
                target_row = existing_by_date[bo_row.posting_date]
                action = "update"
            else:
                target_row = append_pointer
                append_pointer += 1
                action = "append"

            tonnes_cell = self._cell(sheet_name, target_row, col_tonnes)
            metal_cell = self._cell(sheet_name, target_row, col_metal)
            old_tonnes = tonnes_cell.getValue() if action == "update" else None
            old_metal = metal_cell.getValue() if action == "update" else None

            # Tolerance, not exact equality: the BO export and the workbook's own
            # cached values can differ by a few parts in 1e13 (float round-trip
            # noise from independent Excel saves), which is not a real change.
            unchanged = (
                action == "update"
                and old_tonnes is not None
                and old_metal is not None
                and abs(old_tonnes - bo_row.tonnes_cable) < 1e-6
                and abs(old_metal - bo_row.tonnes_metal) < 1e-6
            )
            if unchanged:
                changes.append(
                    RowChange(target_row, "unchanged", bo_row.posting_date,
                              old_tonnes, old_metal, bo_row.tonnes_cable, bo_row.tonnes_metal)
                )
                continue

            changes.append(
                RowChange(target_row, action, bo_row.posting_date,
                          old_tonnes, old_metal, bo_row.tonnes_cable, bo_row.tonnes_metal)
            )

            if action == "append":
                date_cell = self._cell(sheet_name, target_row, col_date)
                date_cell.setValue(_date_to_excel_serial(bo_row.posting_date))
            tonnes_cell.setValue(bo_row.tonnes_cable)
            metal_cell.setValue(bo_row.tonnes_metal)

        return changes

    # -- price refresh: Synthèse!U3 (+ V3 audit tag) ------------------------

    def set_price(self, config: MetalConfig, price: float) -> PriceChange:
        price_row, price_col = self._parse_cell_ref(config.price_cell)
        audit_row, audit_col = self._parse_cell_ref(config.price_audit_cell)
        price_cell = self._cell(config.synthese_sheet, price_row, price_col)
        audit_cell = self._cell(config.synthese_sheet, audit_row, audit_col)

        old_price = price_cell.getValue() or None
        old_audit = audit_cell.getString() or None
        new_audit = date.today().isoformat()

        price_cell.setValue(price)
        audit_cell.setString(new_audit)

        return PriceChange(
            config.price_cell, old_price, price, config.price_audit_cell, old_audit, new_audit
        )

    @staticmethod
    def _parse_cell_ref(ref: str):
        """'U3' -> (row=3, col=21), both 1-indexed for use with _cell()."""
        letters = "".join(ch for ch in ref if ch.isalpha())
        digits = "".join(ch for ch in ref if ch.isdigit())
        col = 0
        for ch in letters.upper():
            col = col * 26 + (ord(ch) - ord("A") + 1)
        return int(digits), col

    # -- recalculation & verification ---------------------------------------

    def recalculate(self):
        self.doc.calculateAll()

    def scan_formula_errors(self, sheet_names: List[str]) -> List[CellError]:
        """Only scans the sheets this tool actually reads/writes (the import
        sheet and Synthèse), not all ~20 legacy year sheets in the workbook --
        old unrelated sheets can carry their own long-standing #REF!/#N/A
        cells that have nothing to do with this run and would just be noise.
        """
        errors: List[CellError] = []
        for sheet_name in sheet_names:
            sheet = self._sheet(sheet_name)
            cursor = sheet.createCursor()
            cursor.gotoEndOfUsedArea(False)
            used = cursor.RangeAddress
            for r in range(used.StartRow, used.EndRow + 1):
                for c in range(used.StartColumn, used.EndColumn + 1):
                    cell = sheet.getCellByPosition(c, r)
                    err = cell.getError()
                    if err != 0:
                        errors.append(CellError(sheet_name, cell.AbsoluteName, err))
        return errors

    # -- reading back for guardrails / email ---------------------------------

    def read_header_status(self, config: MetalConfig) -> HeaderStatus:
        b1 = self._cell(config.import_sheet, 1, 2)
        d1 = self._cell(config.import_sheet, 1, 4)
        workday = b1.getValue() if b1.getError() == 0 and b1.getValue() != 0 else None
        return HeaderStatus(workday_number=workday, as_of_date_text=d1.getString())

    def read_synthese_summary(self, config: MetalConfig) -> SyntheseSummary:
        summary = SyntheseSummary()

        def numeric_or_none(cell):
            if cell.getError() != 0:
                return None
            s = cell.getString()
            if s == "":
                return None
            return cell.getValue()

        for row in range(config.synthese_first_data_row, config.synthese_last_data_row + 1):
            date_cell = self._cell(config.synthese_sheet, row, config.synthese_col_date)
            date_text = date_cell.getString()
            actual = numeric_or_none(self._cell(config.synthese_sheet, row, config.synthese_col_actual))
            if actual is None:
                continue  # no posting recorded for this working day yet
            daily = numeric_or_none(self._cell(config.synthese_sheet, row, config.synthese_col_daily)) or 0.0
            workday = numeric_or_none(self._cell(config.synthese_sheet, row, config.synthese_col_workday))
            forecast = numeric_or_none(self._cell(config.synthese_sheet, row, config.synthese_col_forecast))
            gap = numeric_or_none(self._cell(config.synthese_sheet, row, config.synthese_col_gap))
            summary.daily_rows.append(
                SyntheseDailyRow(date_text, daily, workday, actual, forecast, gap)
            )

        total_row = config.synthese_total_row
        summary.total_actual = numeric_or_none(self._cell(config.synthese_sheet, total_row, config.synthese_col_actual))
        summary.total_workdays = numeric_or_none(self._cell(config.synthese_sheet, total_row, config.synthese_col_workday))
        summary.total_forecast = numeric_or_none(self._cell(config.synthese_sheet, total_row, config.synthese_col_forecast))
        summary.total_gap = numeric_or_none(self._cell(config.synthese_sheet, total_row, config.synthese_col_gap))
        return summary

    def detect_stray_leftover_row(self, config: MetalConfig) -> Optional[int]:
        """Advisory only (not a guardrail): flag the classic leftover-BO-Total
        artifact -- a row right after the last real date whose date cell is
        blank/text but whose tonnes columns are non-zero. It self-heals the
        moment a real new date is appended there, so we only report it."""
        sheet_name = config.import_sheet
        row = config.import_first_data_row
        last_valid_row = row - 1
        while True:
            date_cell = self._cell(sheet_name, row, config.import_col_date)
            tonnes_cell = self._cell(sheet_name, row, config.import_col_tonnes)
            metal_cell = self._cell(sheet_name, row, config.import_col_metal)
            has_date = date_cell.getValue() > 0
            has_leftover_numbers = tonnes_cell.getValue() != 0 or metal_cell.getValue() != 0
            if has_date:
                last_valid_row = row
                row += 1
                continue
            if has_leftover_numbers and row == last_valid_row + 1:
                return row
            break
        return None

    # -- saving ---------------------------------------------------------------

    def save_copy_as(self, out_path: str):
        out_path = os.path.abspath(out_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        url = uno.systemPathToFileUrl(out_path)
        self.doc.storeToURL(url, (_make_prop("FilterName", "Calc MS Excel 2007 XML"),))
