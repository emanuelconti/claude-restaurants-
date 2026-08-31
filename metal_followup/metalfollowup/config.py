"""
Per-metal configuration.

Copper and aluminium go through the exact same code path (bo_import,
workbook_session, guardrails, email_draft). Everything that differs between
the two metals -- sheet names, casing, default price -- lives here in one
place. Porting to Office Scripts later just means porting these constants
into whatever config object that environment uses.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetalConfig:
    key: str                     # "copper" / "aluminium" -- used on the CLI (--metal)
    label_fr: str                # how the metal is named in the workbooks/email ("Cuivre")
    metal_col_header: str        # BO/import-sheet header for the metal-content column

    # --- BO daily export (.xls) ---
    bo_sheet: str                # exact sheet name in the BO export

    # --- Monthly workbook (.xlsx) ---
    import_sheet: str            # sheet name for the daily import block (case differs by metal!)
    synthese_sheet: str = "Synthèse"

    # A:D layout of the import sheet. Row 4 is the first data row; column D is
    # a running-total FORMULA already present in the template and must never
    # be written by this tool.
    import_first_data_row: int = 4
    import_col_date: int = 1     # column A
    import_col_tonnes: int = 2   # column B (cable tonnes)
    import_col_metal: int = 3    # column C (metal-content tonnes)
    import_col_cumulative: int = 4  # column D -- READ ONLY, never write

    # Synthèse cells.
    price_cell: str = "U3"       # COURS CUIVRE / COURS ALU input
    price_audit_cell: str = "V3"  # date the price was set -- our audit tag

    # Synthèse day-by-day analysis block (already built, we only read it).
    synthese_first_data_row: int = 5
    synthese_last_data_row: int = 27
    synthese_total_row: int = 28
    # Columns, 1-indexed (C=3 .. H=8):
    #   C date | D daily tonnes | E working-day count |
    #   F actual cumulative | G forecast cumulative | H gap (forecast - actual)
    synthese_col_date: int = 3
    synthese_col_daily: int = 4
    synthese_col_workday: int = 5
    synthese_col_actual: int = 6
    synthese_col_forecast: int = 7
    synthese_col_gap: int = 8

    default_price: float = 0.0
    default_gap_threshold: float = 50.0  # tonnes; placeholder, adjust per business rule


METALS = {
    "copper": MetalConfig(
        key="copper",
        label_fr="Cuivre",
        metal_col_header="Tonnes Cu",
        bo_sheet="Import par dates",
        import_sheet="import par date",  # lowercase "i" -- exact match required
        default_price=11727.13,
    ),
    "aluminium": MetalConfig(
        key="aluminium",
        label_fr="Aluminium",
        metal_col_header="Tonnes Al",
        bo_sheet="Import par date",
        import_sheet="Import par date",  # capital "I" -- exact match required
        default_price=3166.45,
    ),
}


def get_config(metal_key: str) -> MetalConfig:
    try:
        return METALS[metal_key]
    except KeyError:
        raise SystemExit(
            f"Unknown metal '{metal_key}'. Choose one of: {', '.join(METALS)}"
        )
