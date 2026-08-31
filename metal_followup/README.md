# Metal follow-up test bench

A proof-of-concept that removes the *mechanical* steps of the daily copper/
aluminium follow-up -- pasting the BO export into the monthly workbook,
refreshing the price cell, recalculating, and drafting the status email --
while leaving every analytical and hedging decision to a person.

**This tool never sends an email and never makes a hedging/pre-hedging
decision.** It writes a `.eml` draft for someone to review and send.

It is a prototype meant to prove the logic and be demoed. The production
version will be rebuilt in Office Scripts + Power Automate; see
[Porting to Office Scripts](#porting-to-office-scripts-later) at the bottom.

## What it does, in order

1. Reads the day's Business Objects export (`.xls`) and pulls out the daily
   posting rows (date, cable tonnes, metal tonnes), ignoring the trailing
   "Total" row.
2. Opens a **copy** of the monthly workbook (`.xlsx`) and writes those rows
   into columns A:C of the import sheet, matched by date -- an existing
   partial month is updated in place, a new day is appended. **Column D
   (the running total formula) and every formula on the Synthèse sheet are
   never touched.**
3. Writes the metal price into `Synthèse!U3` and today's date into `V3` as
   an audit tag.
4. Recalculates every formula and checks for formula errors on the sheets it
   touched.
5. Runs four guardrail checks (see below) -- these only ever produce a
   warning, never change a number or skip a step.
6. Builds a `.eml` draft: header line (metal / date / working-day number),
   an HTML table of the Synthèse day-by-day figures (date, actual
   cumulative, forecast, gap), and a warning banner at the top if any
   guardrail failed.
7. If nothing went wrong and it's not a dry run: backs up the *original*
   workbook, then saves the recalculated copy to `output/`.

The original workbook is **never opened for writing** -- every step 2-7 runs
against a throwaway temp copy; only a workbook that recalculated cleanly
(zero formula errors) gets promoted into `output/`.

## Setup

You need:

- Python 3.9+
- **LibreOffice with the Calc component**, not just the base package:
  ```
  sudo apt-get install libreoffice-calc python3-uno
  ```
  (`python3-uno` gives Python the `uno` module used to drive LibreOffice --
  this is what writes into the workbook and recalculates it, instead of a
  library like openpyxl. See [Why UNO, not openpyxl](#why-uno-and-not-openpyxl)
  below for why that matters on these specific files.)
- The Python packages in `requirements.txt`:
  ```
  pip install -r requirements.txt
  ```

No French locale package needs to be installed on the OS -- the tool sets
`LANG`/`LC_ALL=fr_FR.UTF-8` only for the LibreOffice subprocess it launches,
which is enough for LibreOffice's own formula engine even if `fr_FR.UTF-8`
was never generated with `locale-gen`. (This is required: the workbook's own
date formulas use French `TEXT()` format codes like `"jj/mm/aaaa"`, which
raise `#VALUE!` under an English locale.)

## Usage

```
python metal_followup.py --metal copper \
    --bo SuiviCuivre_2026.xls \
    --book Suivi_Cuivre_202607.xlsx \
    --price 11727.13
```

```
python metal_followup.py --metal aluminium \
    --bo Suivi_Alu_26.xls \
    --book Suivi_Alu_202607.xlsx \
    --price 3166.45
```

Useful flags:

- `--dry-run` -- computes and previews everything (including a preview
  `.eml`, named `DRYRUN_...`), but writes nothing to `backups/` or
  `output/`, and never touches the real workbook.
- `--price` is optional -- if omitted, the tool falls back to
  `config/prices.json`, then to the hardcoded default in `config.py`.
- `--price-source lme` is a placeholder for a future live price feed. It is
  **not implemented** on purpose (see `price_source.py`) -- this prototype
  makes no network calls.
- `--gap-threshold 50` overrides the tonnes threshold for the month-to-date
  gap guardrail (default is set per metal in `config.py`).
- `--output-dir` / `--backup-dir` override where the recalculated copy and
  the pre-write backup land (default: `output/` and `backups/` next to this
  README).

Every run prints a step-by-step log: which rows were updated/appended/left
alone, the price that was written, and the pass/fail result of each
guardrail.

## The four guardrails

Guardrails only ever print/display a warning. They never change a figure,
never block a step, never decide anything.

1. **Working days filled** -- every Monday-Friday from the 1st of the month
   up to the last date in the BO export must be present. (No public-holiday
   calendar in this prototype -- same simplification the workbook's own
   `WORKDAY()` formulas make.)
2. **Price freshness** -- the price cell must be non-empty, and its `V3`
   audit tag must be today's date.
3. **Gap threshold** -- `|Synthèse row 28 gap| <= --gap-threshold`.
4. **Sanity check** (bonus, not in the original 3) -- the recalculated
   actual cumulative on Synthèse row 28 should match the BO export's own
   Total row, within rounding. Catches a skipped date or a stray leftover
   row before anyone trusts the numbers.

A failed guardrail puts a red banner at the top of the email draft and a
`[WARN]` line in the console. The subject line also gets an
`[A VERIFIER]` prefix.

## A known leftover-data quirk in these workbooks

Both sample workbooks have a row right after the last real posting date
whose date cell is blank/text (a stray "Total" label, or nothing at all)
but whose tonnes columns are non-zero -- almost certainly because someone
previously pasted the BO export's own Total row in by hand. This tool
detects and reports it (as a console note, not a guardrail) but does not
touch it, because deleting data outside its designated input cells wasn't
asked for. The moment a genuinely new date needs that row, this tool's
append logic overwrites A/B/C there anyway, which clears the leftover for
free.

## Why UNO, not openpyxl

These are real production workbooks with an embedded chart, embedded
images/logos, threaded comments, and a Microsoft Purview sensitivity label.
A plain `openpyxl.load_workbook()` + `.save()` round trip **silently drops
the chart, every embedded image, threaded comments, and the sensitivity
label** -- confirmed by diffing the zip contents of an openpyxl-saved copy
against the original while building this tool. Driving LibreOffice's own
UNO API to make the cell edits *and* do the recalculation in the same
session keeps everything to one, much less lossy, round trip (LibreOffice's
own save still drops a few cosmetic/legacy parts -- print settings, custom
chart colors, some old comment threads -- but keeps the chart, the images,
and the sensitivity label).

## Porting to Office Scripts (later)

This mapping is why the code is organized the way it is -- each module's
job has a near-1:1 Office Scripts/Power Automate equivalent:

| This prototype | Office Scripts + Power Automate |
|---|---|
| `bo_import.py` reads the BO `.xls` with `xlrd`, skips the Total row by checking the date cell's type | A Power Automate flow step reading the export (or an Excel Script `Range.getValues()`), filtering rows where the date parses |
| `workbook_session.apply_bo_rows()` -- match-by-date, update in place / append | `worksheet.getRange(...).getValues()` to read existing dates, then `setValues()` on the matched or next-free row. Column D is still never written. |
| `workbook_session.set_price()` | `worksheet.getRange("U3").setValue(price)` + `getRange("V3").setValue(today)` |
| `workbook_session.recalculate()` + `scan_formula_errors()` | `workbook.application.calculate(ExcelScript.CalculationType.full)`, then check `range.getCellProperties().errorType` |
| `guardrails.py` -- pure comparisons over numbers, no Excel-specific code | Ports almost unchanged into a Power Automate "Condition" step or the tail of the Office Script |
| `email_draft.py` -- writes a `.eml` | Becomes "Create draft" in the Outlook connector, using the same header/table/warning content |
| The LibreOffice recalculation step entirely | Not needed -- Excel Online recalculates live; this step only exists because this prototype runs headless outside of Excel |

The one piece that has **no** Office Scripts equivalent and should be
dropped, not ported, is `workbook_session.py`'s LibreOffice process
management (starting `soffice`, connecting over UNO). That machinery exists
only because this prototype isn't running inside Excel.

## Project layout

```
metal_followup.py          entry point / CLI
metalfollowup/
  config.py                per-metal configuration (the only place that differs between copper and aluminium)
  bo_import.py             read the BO .xls date block
  price_source.py          price resolution (CLI > config file > default); LME stub kept isolated
  workbook_session.py       all .xlsx reading/writing/recalculating, via LibreOffice UNO
  guardrails.py            the four checks
  email_draft.py           builds the .eml draft
  cli.py                   orchestration
config/prices.json         small fallback price config
output/                    recalculated workbook copies + .eml drafts land here (gitignored)
backups/                   pre-write backups of the original workbook land here (gitignored)
```
