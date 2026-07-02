#!/usr/bin/env python3
"""Generate the ZenBudget Excel finance planner (the actual sellable product)."""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.chart import PieChart, BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, DataBarRule
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime

# ── PALETTE ──────────────────────────────────────────────────────────────────
INK      = "1F2430"
MUTED    = "6B7280"
ACCENT   = "10B981"   # green
ACCENT2  = "3B82F6"   # blue
WARN     = "F59E0B"
DANGER   = "EF4444"
BG_SOFT  = "F3F4F6"
WHITE    = "FFFFFF"

HEADER_FILL = PatternFill("solid", fgColor=INK)
HEADER_FONT = Font(color=WHITE, bold=True, size=11, name="Calibri")
TITLE_FONT  = Font(color=INK, bold=True, size=20, name="Calibri")
SUB_FONT    = Font(color=MUTED, size=11, name="Calibri")
LABEL_FONT  = Font(color=INK, bold=True, size=11, name="Calibri")
BODY_FONT   = Font(color=INK, size=11, name="Calibri")
THIN = Side(style="thin", color="E5E7EB")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

EXPENSE_CATEGORIES = [
    "Housing (rent/mortgage)", "Utilities", "Groceries", "Transport",
    "Insurance", "Debt payments", "Subscriptions", "Health", "Entertainment",
    "Shopping", "Dining out", "Savings/Investing", "Other",
]


def style_header_row(ws, row, n_cols, start_col=1):
    for c in range(start_col, start_col + n_cols):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", horizontal="left" if c == start_col else "center")
        cell.border = BORDER_ALL


def title_block(ws, title, subtitle, row=1):
    ws.cell(row=row, column=1, value=title).font = TITLE_FONT
    ws.cell(row=row + 1, column=1, value=subtitle).font = SUB_FONT


def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ── BUILD WORKBOOK ────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()

# ── 1. DASHBOARD ─────────────────────────────────────────────────────────────
dash = wb.active
dash.title = "Dashboard"
dash.sheet_view.showGridLines = False
title_block(dash, "ZenBudget", "Your finances, on one page.", row=2)

labels = [("Monthly income (from Transactions)", '=SUMIF(Transactions!D:D,"Income",Transactions!E:E)'),
          ("Monthly expenses (planned)", "=SUM('Monthly Budget'!C4:C16)"),
          ("Monthly expenses (actual, from Transactions)", '=SUMIF(Transactions!D:D,"Expense",Transactions!E:E)'),
          ("Savings rate", "=IFERROR((B5-B7)/B5,0)")]

r = 5
for i, (label, formula) in enumerate(labels):
    row = r + i
    dash.cell(row=row, column=1, value=label).font = LABEL_FONT
    cell = dash.cell(row=row, column=2, value=formula)
    cell.font = Font(bold=True, size=13, color=ACCENT if i < 3 else ACCENT2)
    if i == 3:
        cell.number_format = "0.0%"
    else:
        cell.number_format = "#,##0.00"

dash.cell(row=11, column=1, value="Top expense categories this month").font = LABEL_FONT
dash.cell(row=12, column=1, value="Category").font = Font(bold=True)
dash.cell(row=12, column=2, value="Actual").font = Font(bold=True)
for i, cat in enumerate(EXPENSE_CATEGORIES):
    row = 13 + i
    dash.cell(row=row, column=1, value=cat)
    dash.cell(row=row, column=2, value=f"='Monthly Budget'!E{4+i}")
    dash.cell(row=row, column=2).number_format = "#,##0.00"

pie = PieChart()
pie.title = "Where your money goes"
data = Reference(dash, min_col=2, min_row=12, max_row=12 + len(EXPENSE_CATEGORIES))
cats = Reference(dash, min_col=1, min_row=13, max_row=12 + len(EXPENSE_CATEGORIES))
pie.add_data(data, titles_from_data=True)
pie.set_categories(cats)
pie.height, pie.width = 9, 12
dash.add_chart(pie, "D5")

autosize(dash, [30, 16])

# ── 2. MONTHLY BUDGET ─────────────────────────────────────────────────────────
mb = wb.create_sheet("Monthly Budget")
mb.sheet_view.showGridLines = False
title_block(mb, "Monthly Budget", "Plan vs. actual, by category.")
mb.cell(row=3, column=1, value="Category")
mb.cell(row=3, column=2, value="")
mb.cell(row=3, column=3, value="Planned")
mb.cell(row=3, column=4, value="Actual")
mb.cell(row=3, column=5, value="Difference")
style_header_row(mb, 3, 5)

for i, cat in enumerate(EXPENSE_CATEGORIES):
    row = 4 + i
    mb.cell(row=row, column=1, value=cat).border = BORDER_ALL
    mb.cell(row=row, column=2).border = BORDER_ALL
    mb.cell(row=row, column=3, value=0).number_format = "#,##0.00"
    mb.cell(row=row, column=4, value=0).number_format = "#,##0.00"
    mb.cell(row=row, column=5, value=f"=C{row}-D{row}").number_format = "#,##0.00"
    for c in (3, 4, 5):
        mb.cell(row=row, column=c).border = BORDER_ALL

total_row = 4 + len(EXPENSE_CATEGORIES)
mb.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)
mb.cell(row=total_row, column=3, value=f"=SUM(C4:C{total_row-1})").font = Font(bold=True)
mb.cell(row=total_row, column=4, value=f"=SUM(D4:D{total_row-1})").font = Font(bold=True)
mb.cell(row=total_row, column=5, value=f"=C{total_row}-D{total_row}").font = Font(bold=True)
for c in (3, 4, 5):
    mb.cell(row=total_row, column=c).number_format = "#,##0.00"

diff_range = f"E4:E{total_row-1}"
mb.conditional_formatting.add(diff_range, CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor="FEE2E2")))
mb.conditional_formatting.add(diff_range, CellIsRule(operator="greaterThanOrEqual", formula=["0"], fill=PatternFill("solid", fgColor="D1FAE5")))

autosize(mb, [28, 4, 14, 14, 14])

# ── 3. TRANSACTIONS ───────────────────────────────────────────────────────────
tx = wb.create_sheet("Transactions")
tx.sheet_view.showGridLines = False
title_block(tx, "Transactions", "Log every expense and income entry here.")
headers = ["Date", "Description", "Category", "Type", "Amount"]
for i, h in enumerate(headers, start=1):
    tx.cell(row=3, column=i, value=h)
style_header_row(tx, 3, len(headers))

for row in range(4, 104):
    for c in range(1, 6):
        tx.cell(row=row, column=c).border = BORDER_ALL
    tx.cell(row=row, column=5).number_format = "#,##0.00"

dv_type = DataValidation(type="list", formula1='"Income,Expense"', allow_blank=True)
tx.add_data_validation(dv_type)
dv_type.add(f"D4:D103")

dv_cat = DataValidation(type="list", formula1='"' + ",".join(EXPENSE_CATEGORIES + ["Income"]) + '"', allow_blank=True)
tx.add_data_validation(dv_cat)
dv_cat.add(f"C4:C103")

autosize(tx, [14, 32, 26, 12, 14])

# ── 4. SAVINGS GOALS ──────────────────────────────────────────────────────────
sg = wb.create_sheet("Savings Goals")
sg.sheet_view.showGridLines = False
title_block(sg, "Savings Goals", "Track progress toward what matters.")
headers = ["Goal", "Target amount", "Saved so far", "Progress", "Target date"]
for i, h in enumerate(headers, start=1):
    sg.cell(row=3, column=i, value=h)
style_header_row(sg, 3, len(headers))

for row in range(4, 14):
    sg.cell(row=row, column=2).number_format = "#,##0.00"
    sg.cell(row=row, column=3).number_format = "#,##0.00"
    sg.cell(row=row, column=4, value=f"=IFERROR(C{row}/B{row},0)").number_format = "0%"
    sg.cell(row=row, column=5).number_format = "yyyy-mm-dd"
    for c in range(1, 6):
        sg.cell(row=row, column=c).border = BORDER_ALL

sg.conditional_formatting.add(
    f"D4:D13",
    DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=ACCENT)
)
autosize(sg, [26, 16, 16, 12, 16])

# ── 5. DEBT PAYOFF ─────────────────────────────────────────────────────────────
dp = wb.create_sheet("Debt Payoff")
dp.sheet_view.showGridLines = False
title_block(dp, "Debt Payoff Tracker", "See the finish line.")
headers = ["Debt", "Balance", "Interest rate (APR)", "Minimum payment", "Months to payoff (est.)"]
for i, h in enumerate(headers, start=1):
    dp.cell(row=3, column=i, value=h)
style_header_row(dp, 3, len(headers))

for row in range(4, 12):
    dp.cell(row=row, column=2).number_format = "#,##0.00"
    dp.cell(row=row, column=3).number_format = "0.0%"
    dp.cell(row=row, column=4).number_format = "#,##0.00"
    dp.cell(row=row, column=5, value=f"=IFERROR(B{row}/D{row},0)").number_format = "0"
    for c in range(1, 6):
        dp.cell(row=row, column=c).border = BORDER_ALL

autosize(dp, [24, 14, 16, 16, 20])

# ── 6. SUBSCRIPTIONS ───────────────────────────────────────────────────────────
sub = wb.create_sheet("Subscriptions")
sub.sheet_view.showGridLines = False
title_block(sub, "Subscription Tracker", "Find the money leaks.")
headers = ["Service", "Monthly cost", "Billing cycle", "Next charge", "Annual cost"]
for i, h in enumerate(headers, start=1):
    sub.cell(row=3, column=i, value=h)
style_header_row(sub, 3, len(headers))

for row in range(4, 20):
    sub.cell(row=row, column=2).number_format = "#,##0.00"
    sub.cell(row=row, column=4).number_format = "yyyy-mm-dd"
    sub.cell(row=row, column=5, value=f"=B{row}*12").number_format = "#,##0.00"
    for c in range(1, 6):
        sub.cell(row=row, column=c).border = BORDER_ALL

dv_cycle = DataValidation(type="list", formula1='"Monthly,Yearly,Weekly"', allow_blank=True)
sub.add_data_validation(dv_cycle)
dv_cycle.add("C4:C19")

total_row = 20
sub.cell(row=total_row, column=1, value="TOTAL ANNUAL COST").font = Font(bold=True)
sub.cell(row=total_row, column=5, value=f"=SUM(E4:E19)").font = Font(bold=True)
sub.cell(row=total_row, column=5).number_format = "#,##0.00"

autosize(sub, [24, 14, 14, 16, 14])

# ── 7. YEARLY OVERVIEW ─────────────────────────────────────────────────────────
yo = wb.create_sheet("Yearly Overview")
yo.sheet_view.showGridLines = False
title_block(yo, "Yearly Overview", "The 12-month picture.")
headers = ["Month", "Income", "Expenses", "Net savings"]
for i, h in enumerate(headers, start=1):
    yo.cell(row=3, column=i, value=h)
style_header_row(yo, 3, len(headers))

for i, month in enumerate(MONTHS):
    row = 4 + i
    yo.cell(row=row, column=1, value=month)
    yo.cell(row=row, column=2, value=0).number_format = "#,##0.00"
    yo.cell(row=row, column=3, value=0).number_format = "#,##0.00"
    yo.cell(row=row, column=4, value=f"=B{row}-C{row}").number_format = "#,##0.00"
    for c in range(1, 5):
        yo.cell(row=row, column=c).border = BORDER_ALL

chart = LineChart()
chart.title = "Net savings over the year"
data = Reference(yo, min_col=4, min_row=3, max_row=15)
cats = Reference(yo, min_col=1, min_row=4, max_row=15)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height, chart.width = 9, 18
yo.add_chart(chart, "F3")

autosize(yo, [14, 14, 14, 14])

# ── COVER / HOW TO USE ─────────────────────────────────────────────────────────
cover = wb.create_sheet("How to use", 0)
cover.sheet_view.showGridLines = False
cover.sheet_properties.tabColor = ACCENT
title_block(cover, "ZenBudget", "The finance planner that fits on one screen.", row=2)
instructions = [
    "1. Start in 'Monthly Budget' — set your planned amount per category.",
    "2. Log every expense in 'Transactions' as it happens.",
    "3. Fill in the 'Actual' column in 'Monthly Budget' at the end of the month",
    "   (or use =SUMIF('Transactions'!C:C, category, 'Transactions'!E:E) to automate it).",
    "4. Check 'Dashboard' any time for your savings rate and spending breakdown.",
    "5. Track goals in 'Savings Goals' and debts in 'Debt Payoff'.",
    "6. Review 'Subscriptions' monthly — this tab alone usually pays for the planner.",
    "7. At year end, fill in 'Yearly Overview' for the full 12-month picture.",
    "",
    "Tip: duplicate the 'Monthly Budget' tab each month if you want a full history.",
]
for i, line in enumerate(instructions):
    cover.cell(row=6 + i, column=1, value=line).font = BODY_FONT
autosize(cover, [90])

wb.move_sheet("Dashboard", offset=0)

OUT = "ZenBudget_Planner.xlsx"
wb.save(OUT)
print(f"Saved {OUT}")
