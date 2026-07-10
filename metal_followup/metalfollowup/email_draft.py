"""
Build the daily follow-up email as a .eml draft -- never sent.

A person opens the draft, reviews the numbers and the guardrail warnings (if
any), edits as needed, and sends it themselves. This module has no send
capability at all, on purpose: the hedging/pre-hedging decision the email
supports is explicitly out of scope for automation.

Office Scripts port note: in the Power Automate version, this becomes
"create draft" (Outlook connector) instead of writing a .eml file, using the
same header/table/warnings content assembled the same way.
"""

from datetime import date
from email.message import EmailMessage
from html import escape
from typing import List, Optional

from .config import MetalConfig
from .guardrails import Guardrail
from .workbook_session import HeaderStatus, PriceChange, SyntheseSummary


def _fmt(value: Optional[float], decimals: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value:,.{decimals}f}".replace(",", " ")


def _build_html(
    config: MetalConfig,
    header_status: HeaderStatus,
    synthese_summary: SyntheseSummary,
    guardrails: List[Guardrail],
    price_change: PriceChange,
) -> str:
    failed = [g for g in guardrails if not g.passed]

    warning_html = ""
    if failed:
        items = "".join(f"<li>{escape(g.message)}</li>" for g in failed)
        warning_html = f"""
        <div style="border:2px solid #c0392b;background:#fdecea;padding:10px 14px;margin-bottom:16px;">
          <strong style="color:#c0392b;">⚠ Guardrail warning(s) -- review before sending</strong>
          <ul style="margin:6px 0 0 18px;">{items}</ul>
        </div>
        """

    table_style = "border-collapse:collapse;font-family:Calibri,Arial,sans-serif;font-size:13px;"
    cell_style = "border:1px solid #ccc;padding:4px 10px;"
    right_cell_style = cell_style + "text-align:right;"

    rows_html = ""
    for row in synthese_summary.daily_rows:
        rows_html += f"""
        <tr>
          <td style="{cell_style}">{escape(row.date_text)}</td>
          <td style="{right_cell_style}">{_fmt(row.actual_cumulative)}</td>
          <td style="{right_cell_style}">{_fmt(row.forecast_cumulative)}</td>
          <td style="{right_cell_style}">{_fmt(row.gap)}</td>
        </tr>
        """

    total_row_html = f"""
    <tr style="font-weight:bold;border-top:2px solid #333;">
      <td style="{cell_style}">Total</td>
      <td style="{right_cell_style}">{_fmt(synthese_summary.total_actual)}</td>
      <td style="{right_cell_style}">{_fmt(synthese_summary.total_forecast)}</td>
      <td style="{right_cell_style}">{_fmt(synthese_summary.total_gap)}</td>
    </tr>
    """

    return f"""
    <html><body style="font-family:Calibri,Arial,sans-serif;font-size:13px;">
    {warning_html}
    <p><strong>Suivi {escape(config.label_fr)} -- au {escape(header_status.as_of_date_text)}
    -- jour ouvré n°{_fmt(header_status.workday_number, 0)}</strong></p>

    <table style="{table_style}">
      <thead>
        <tr style="background:#eee;">
          <th style="{cell_style}text-align:left;">Date</th>
          <th style="{cell_style}text-align:right;">Réel cumulé (t)</th>
          <th style="{cell_style}text-align:right;">Prévision cumulée (t)</th>
          <th style="{cell_style}text-align:right;">Écart (t)</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
        {total_row_html}
      </tbody>
    </table>

    <p>
      Prix utilisé (Synthèse!{config.price_cell}) : {price_change.new_price} --
      relevé le {price_change.new_audit}.
    </p>

    <p style="color:#888;font-size:11px;">
      Brouillon généré automatiquement -- à relire avant envoi. Aucune décision
      de couverture n'a été prise par cet outil.
    </p>
    </body></html>
    """


def _build_text(
    config: MetalConfig,
    header_status: HeaderStatus,
    synthese_summary: SyntheseSummary,
    guardrails: List[Guardrail],
    price_change: PriceChange,
) -> str:
    lines = []
    failed = [g for g in guardrails if not g.passed]
    if failed:
        lines.append("*** GUARDRAIL WARNING(S) -- REVIEW BEFORE SENDING ***")
        for g in failed:
            lines.append(f"  - {g.message}")
        lines.append("")

    lines.append(
        f"Suivi {config.label_fr} -- au {header_status.as_of_date_text} "
        f"-- jour ouvré n°{_fmt(header_status.workday_number, 0)}"
    )
    lines.append("")
    lines.append(f"{'Date':<14}{'Réel cumulé':>14}{'Prévision':>14}{'Écart':>10}")
    for row in synthese_summary.daily_rows:
        lines.append(
            f"{row.date_text:<14}{_fmt(row.actual_cumulative):>14}"
            f"{_fmt(row.forecast_cumulative):>14}{_fmt(row.gap):>10}"
        )
    lines.append(
        f"{'Total':<14}{_fmt(synthese_summary.total_actual):>14}"
        f"{_fmt(synthese_summary.total_forecast):>14}{_fmt(synthese_summary.total_gap):>10}"
    )
    lines.append("")
    lines.append(
        f"Prix utilisé (Synthèse!{config.price_cell}): {price_change.new_price} "
        f"-- relevé le {price_change.new_audit}."
    )
    lines.append("")
    lines.append("Brouillon généré automatiquement -- à relire avant envoi.")
    return "\n".join(lines)


def build_email_draft(
    config: MetalConfig,
    header_status: HeaderStatus,
    synthese_summary: SyntheseSummary,
    guardrails: List[Guardrail],
    price_change: PriceChange,
    run_date: date,
    output_path: str,
) -> str:
    failed = [g for g in guardrails if not g.passed]
    subject_prefix = "[A VERIFIER] " if failed else ""
    subject = (
        f"{subject_prefix}Suivi {config.label_fr} -- {header_status.as_of_date_text} "
        f"-- J{_fmt(header_status.workday_number, 0)}"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "brouillon@localhost"  # placeholder; a human sends this, not this tool
    msg["To"] = ""
    msg["Date"] = run_date.isoformat()
    msg.set_content(_build_text(config, header_status, synthese_summary, guardrails, price_change))
    msg.add_alternative(
        _build_html(config, header_status, synthese_summary, guardrails, price_change),
        subtype="html",
    )

    with open(output_path, "wb") as f:
        f.write(bytes(msg))

    return output_path
