"""PDF export for FuzzyMIP reports."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import BinaryIO
from xml.sax.saxutils import escape

import pandas as pd

from .constants import APP_NAME, APP_OWNER_LABEL
from .core import consultive_conclusion, format_fuzzy_value


def write_pdf_report(
    output: str | BinaryIO,
    *,
    project: dict,
    actions: pd.DataFrame,
    ranking: pd.DataFrame,
) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm)
    story = []

    def paragraph(text: object, style: str = "Normal") -> Paragraph:
        return Paragraph(escape(str(text)), styles[style])

    def priority_color(result: object):
        text = str(result).lower()
        if "critico" in text or "prioritaria" in text:
            return colors.HexColor("#fee2e2")
        if "relevante" in text or "potencial" in text:
            return colors.HexColor("#ffedd5")
        if "monitor" in text:
            return colors.HexColor("#fef9c3")
        return None

    def table(rows: list[list[object]], widths: list[float], row_backgrounds: list[object | None] | None = None) -> Table:
        wrapped = [[paragraph(value) for value in row] for row in rows]
        t = Table(wrapped, colWidths=widths, repeatRows=1)
        commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9ca3af")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        if row_backgrounds:
            for row_index, background in enumerate(row_backgrounds, start=1):
                if background is not None:
                    commands.append(("BACKGROUND", (0, row_index), (-1, row_index), background))
        t.setStyle(TableStyle(commands))
        return t

    story.append(paragraph(APP_NAME, "Title"))
    story.append(paragraph("Relatorio consultivo de priorizacao fuzzy por Impacto e Probabilidade", "Heading2"))
    story.append(paragraph(APP_OWNER_LABEL))
    story.append(paragraph(f"Data de geracao: {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
    story.append(Spacer(1, 10))

    story.append(paragraph("1. Projeto", "Heading1"))
    project_rows = [["Campo", "Valor"]]
    for key, value in project.items():
        project_rows.append([key, value])
    story.append(table(project_rows, [4 * cm, 11.7 * cm]))
    story.append(Spacer(1, 10))

    story.append(paragraph("2. Acoes avaliadas", "Heading1"))
    action_rows = [["Acao", "Natureza", "Impacto", "Probabilidade", "Base da informacao"]]
    result_by_action = {
        str(row.get("Acao", "")): row.get("Resultado", "")
        for _, row in ranking.iterrows()
    }
    action_backgrounds = []
    for _, row in actions.iterrows():
        action_name = row.get("Acao", "")
        action_rows.append(
            [
                action_name,
                row.get("Natureza", ""),
                format_fuzzy_value(row.get("Impacto", "")),
                format_fuzzy_value(row.get("Probabilidade", "")),
                row.get("Base da informacao", ""),
            ]
        )
        action_backgrounds.append(priority_color(result_by_action.get(str(action_name), "")))
    story.append(table(action_rows, [4.2 * cm, 2.3 * cm, 2.8 * cm, 2.8 * cm, 3.6 * cm], action_backgrounds))
    story.append(Spacer(1, 10))

    story.append(paragraph("3. Ranking fuzzy Impacto/Probabilidade", "Heading1"))
    rank_rows = [["Rank", "Acao", "Natureza", "Resultado", "Indice ajustado", "Acao recomendada"]]
    ranking_backgrounds = []
    for _, row in ranking.iterrows():
        result = row.get("Resultado", "")
        rank_rows.append(
            [
                row.get("Ranking", ""),
                row.get("Acao", ""),
                row.get("Natureza", ""),
                result,
                f"{float(row.get('Indice ajustado', row.get('Indice I/P', 0.0))):.4f}",
                row.get("Acao recomendada", ""),
            ]
        )
        ranking_backgrounds.append(priority_color(result))
    story.append(table(rank_rows, [1.2 * cm, 3.3 * cm, 2.5 * cm, 2.1 * cm, 2.0 * cm, 4.6 * cm], ranking_backgrounds))
    story.append(Spacer(1, 10))

    story.append(paragraph("Conclusao consultiva", "Heading1"))
    story.append(paragraph(consultive_conclusion(ranking)))

    doc.build(story)


def pdf_bytes(**kwargs) -> bytes:
    buffer = BytesIO()
    write_pdf_report(buffer, **kwargs)
    return buffer.getvalue()
