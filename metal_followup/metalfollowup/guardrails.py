"""
Guardrails: checks that flag problems for a human to look at. They never
change a number, never skip a step, and never decide anything -- they only
add a warning line to the console and to the top of the email draft.

Four checks, matching the task brief:
  1. every working day up to the "as of" date is present in the BO import
  2. the price cell is populated and its audit tag says "today"
  3. the month-to-date gap (Synthèse row 28, forecast - actual) hasn't
     crossed the configured threshold
  4. (bonus sanity check) the workbook's recalculated actual cumulative
     roughly matches the BO export's own Total row -- catches the case
     where a date got missed or a stray leftover row confused the sum

Office Scripts port note: these are plain comparisons over already-computed
numbers -- no UNO/openpyxl-specific code here, so this module ports as-is
(just swap datetime handling for whatever the Power Automate flow uses).
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

from .bo_import import BoRow
from .workbook_session import PriceChange, SyntheseSummary


@dataclass
class Guardrail:
    passed: bool
    message: str


def _expected_workdays(month_start: date, as_of: date) -> List[date]:
    """Mon-Fri only -- same rule the workbook's own WORKDAY() formulas use.
    No French public-holiday calendar in this prototype; a real deployment
    would want one (WORKDAY() in Excel/Office Scripts both accept a holiday
    list -- add it there and here in step with each other)."""
    days = []
    d = month_start
    while d <= as_of:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def check_working_days_filled(bo_rows: List[BoRow], as_of_date: Optional[date]) -> Guardrail:
    if not bo_rows:
        return Guardrail(False, "No posting days found in the BO export at all.")
    if as_of_date is None:
        as_of_date = bo_rows[-1].posting_date

    month_start = as_of_date.replace(day=1)
    expected = _expected_workdays(month_start, as_of_date)
    present = {row.posting_date for row in bo_rows}
    missing = [d for d in expected if d not in present]

    if missing:
        missing_str = ", ".join(d.isoformat() for d in missing)
        return Guardrail(False, f"Missing working day(s) in the BO import: {missing_str}")
    return Guardrail(True, f"All {len(expected)} working day(s) up to {as_of_date.isoformat()} are present.")


def check_price_fresh(price_change: PriceChange, run_date: date) -> Guardrail:
    if not price_change.new_price:
        return Guardrail(False, "Price cell would be empty or zero -- not a usable price.")
    if price_change.new_audit != run_date.isoformat():
        return Guardrail(False, f"Price audit date is {price_change.new_audit}, not today ({run_date.isoformat()}).")
    return Guardrail(True, f"Price cell set to {price_change.new_price} with today's audit date.")


def check_gap_threshold(total_gap: Optional[float], threshold: float) -> Guardrail:
    if total_gap is None:
        return Guardrail(False, "Could not read the month-to-date gap from Synthèse row 28.")
    if abs(total_gap) > threshold:
        return Guardrail(
            False,
            f"Month-to-date gap is {total_gap:+.1f} t, beyond the {threshold:.1f} t threshold.",
        )
    return Guardrail(True, f"Month-to-date gap is {total_gap:+.1f} t, within the {threshold:.1f} t threshold.")


def check_actual_matches_bo_total(bo_rows: List[BoRow], synthese_summary: SyntheseSummary) -> Guardrail:
    bo_total_metal = sum(row.tonnes_metal for row in bo_rows)
    actual = synthese_summary.total_actual
    if actual is None:
        return Guardrail(False, "Synthèse row 28 actual cumulative is blank/error -- cannot sanity-check against the BO Total row.")
    diff = actual - bo_total_metal
    if abs(diff) > 0.5:  # tonnes; loose tolerance for rounding in Synthèse's own ROUND()
        return Guardrail(
            False,
            f"Synthèse actual cumulative ({actual:.2f} t) differs from the BO Total row "
            f"({bo_total_metal:.2f} t) by {diff:+.2f} t. Check for a missed date or a stray leftover row.",
        )
    return Guardrail(True, f"Synthèse actual cumulative matches the BO Total row (within rounding).")


def run_guardrails(
    bo_rows: List[BoRow],
    as_of_date: Optional[date],
    price_change: PriceChange,
    synthese_summary: SyntheseSummary,
    gap_threshold: float,
    run_date: date,
) -> List[Guardrail]:
    return [
        check_working_days_filled(bo_rows, as_of_date),
        check_price_fresh(price_change, run_date),
        check_gap_threshold(synthese_summary.total_gap, gap_threshold),
        check_actual_matches_bo_total(bo_rows, synthese_summary),
    ]
