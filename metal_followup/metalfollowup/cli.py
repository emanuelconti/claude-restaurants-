"""
Command-line entry point. Wires together the modules in this package:

  1. read the BO daily export                              (bo_import)
  2. work on a throwaway copy of the monthly workbook       (workbook_session)
  3. write A:C + the price cell, recalculate, check errors  (workbook_session)
  4. run the guardrails over the recalculated numbers       (guardrails)
  5. write the .eml draft                                   (email_draft)
  6. only if not --dry-run and there are zero formula errors:
     back up the original, then persist the recalculated copy to output/

Nothing here ever opens the original workbook for writing -- only a copy in
a temp directory is ever mutated, and that copy is only promoted to the
output/ folder once we've confirmed the recalculation is clean.
"""

import argparse
import os
import shutil
import sys
import tempfile
from datetime import date, datetime
from typing import Optional

from .bo_import import read_bo_daily_rows
from .config import get_config
from .email_draft import build_email_draft
from .guardrails import Guardrail, run_guardrails
from .price_source import resolve_price
from .workbook_session import WorkbookSession

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)


def _parse_fr_date(text: str) -> Optional[date]:
    """Parse the 'jj/mm/aaaa' text produced by the workbook's own D1 formula."""
    try:
        d, m, y = text.strip().split("/")
        return date(int(y), int(m), int(d))
    except (ValueError, AttributeError):
        return None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metal_followup.py",
        description="Daily metal follow-up test bench: BO import, price refresh, "
        "recalculation, guardrails, and an email draft. No hedging decision is made here.",
    )
    parser.add_argument("--metal", required=True, choices=["copper", "aluminium"])
    parser.add_argument("--bo", required=True, help="Path to the BO daily export (.xls)")
    parser.add_argument("--book", required=True, help="Path to the monthly workbook (.xlsx)")
    parser.add_argument("--price", type=float, default=None, help="Metal price to write to Synthèse!U3")
    parser.add_argument(
        "--price-source",
        choices=["none", "lme"],
        default="none",
        help="'lme' would call a live price feed -- not implemented in this prototype, kept isolated on purpose",
    )
    parser.add_argument(
        "--price-config",
        default=os.path.join(PROJECT_ROOT, "config", "prices.json"),
        help="Fallback price config file, used if --price is not given",
    )
    parser.add_argument(
        "--gap-threshold",
        type=float,
        default=None,
        help="Absolute month-to-date gap (tonnes) above which the gap guardrail warns. "
        "Defaults to the per-metal value in config.py.",
    )
    parser.add_argument("--output-dir", default=os.path.join(PROJECT_ROOT, "output"))
    parser.add_argument("--backup-dir", default=os.path.join(PROJECT_ROOT, "backups"))
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print/preview everything, but write nothing to the workbook, "
        "backups/, or output/. A preview .eml is still written, clearly marked as a dry run.",
    )
    return parser


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    config = get_config(args.metal)
    run_date = date.today()

    print(f"[1/6] Reading BO export: {args.bo} (sheet '{config.bo_sheet}')")
    bo_rows = read_bo_daily_rows(args.bo, config.bo_sheet)
    print(f"       {len(bo_rows)} posting day(s) found, "
          f"{bo_rows[0].posting_date} .. {bo_rows[-1].posting_date}" if bo_rows else "       none found")

    price = resolve_price(
        args.metal, args.price, args.price_config, use_live_source=(args.price_source == "lme")
    )
    gap_threshold = args.gap_threshold if args.gap_threshold is not None else config.default_gap_threshold

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.backup_dir, exist_ok=True)

    book_name = os.path.basename(args.book)
    stem, ext = os.path.splitext(book_name)
    output_book_path = os.path.join(args.output_dir, f"{stem}_{run_date.isoformat()}{ext}")
    backup_path = os.path.join(args.backup_dir, f"{stem}_backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}{ext}")
    eml_name = f"{'DRYRUN_' if args.dry_run else ''}{config.key}_{run_date.isoformat()}_draft.eml"
    eml_path = os.path.join(args.output_dir, eml_name)

    tmp_dir = tempfile.mkdtemp(prefix="metal_followup_")
    tmp_book = os.path.join(tmp_dir, book_name)
    shutil.copy2(args.book, tmp_book)  # never open the original -- always a copy

    try:
        print(f"[2/6] Opening working copy in LibreOffice: {tmp_book}")
        with WorkbookSession(tmp_book) as session:
            print(f"[3/6] Writing BO rows into '{config.import_sheet}'!A:C ...")
            bo_changes = session.apply_bo_rows(config, bo_rows)
            for change in bo_changes:
                if change.action == "unchanged":
                    continue
                print(
                    f"       row {change.row}: {change.action:>6} -- {change.posting_date} "
                    f"tonnes={change.new_tonnes:.3f} metal={change.new_metal:.3f}"
                )
            if all(c.action == "unchanged" for c in bo_changes):
                print("       nothing to update -- workbook already matches the BO export.")

            stray_row = session.detect_stray_leftover_row(config)
            if stray_row:
                print(
                    f"       note: row {stray_row} has non-date leftover data in B/C "
                    f"(likely an old BO 'Total' row pasted by hand). Left untouched; "
                    f"will self-correct once a real new date is appended there."
                )

            print(f"       Setting price Synthèse!{config.price_cell} = {price}")
            price_change = session.set_price(config, price)

            print("[4/6] Recalculating all formulas ...")
            session.recalculate()

            errors = session.scan_formula_errors([config.import_sheet, config.synthese_sheet])
            header_status = session.read_header_status(config)
            synthese_summary = session.read_synthese_summary(config)

            as_of_date = _parse_fr_date(header_status.as_of_date_text) or (
                bo_rows[-1].posting_date if bo_rows else run_date
            )

            print("[5/6] Running guardrails ...")
            guardrails = run_guardrails(
                bo_rows, as_of_date, price_change, synthese_summary, gap_threshold, run_date
            )
            if errors:
                sample = "; ".join(f"{e.sheet}!{e.cell} (code {e.error_code})" for e in errors[:5])
                more = f" (+{len(errors) - 5} more)" if len(errors) > 5 else ""
                guardrails.append(
                    Guardrail(False, f"{len(errors)} formula error cell(s) found: {sample}{more}")
                )
            for g in guardrails:
                status = "OK  " if g.passed else "WARN"
                print(f"       [{status}] {g.message}")

            print(f"[6/6] Building email draft: {eml_path}")
            build_email_draft(
                config, header_status, synthese_summary, guardrails, price_change, run_date, eml_path
            )

            can_save = (not args.dry_run) and (not errors)
            if can_save:
                print(f"       Backing up original to {backup_path}")
                shutil.copy2(args.book, backup_path)
                print(f"       Saving recalculated workbook copy to {output_book_path}")
                session.save_copy_as(output_book_path)
            elif args.dry_run:
                print("       DRY RUN -- workbook and backups untouched. No changes were saved.")
            else:
                print("       NOT SAVED -- formula errors were detected; fix the workbook and re-run.")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\nDone. Review the draft before sending -- this tool never sends email "
          "and never makes a hedging decision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
