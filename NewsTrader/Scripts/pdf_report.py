"""PDF report generation using ReportLab."""
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def create_pdf(filename, item):
    """Generate a PDF report for a single asset analysis."""
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "CompactTitle", parent=styles["Heading1"], fontSize=14, spaceAfter=6
    )
    normal_style = ParagraphStyle(
        "CompactNormal", parent=styles["Normal"], fontSize=9, leading=11
    )
    header_style = ParagraphStyle(
        "CompactHeader", parent=styles["Heading2"], fontSize=11, spaceAfter=4, spaceBefore=6
    )

    asset_name = item.get("Asset") or item.get("Ticker") or "Unknown Asset"
    story.append(Paragraph(f"Analysis: {asset_name}", title_style))
    story.append(
        Paragraph(f"Date: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", normal_style)
    )
    story.append(Spacer(1, 6))

    if "Ticker" in item:
        story.append(Paragraph(f"<b>Ticker:</b> {item['Ticker']}", normal_style))

    rec = item.get("Recommendation") or item.get("Empfehlung")
    if rec:
        rec_color = "black"
        rec_text = str(rec).lower()
        if "buy" in rec_text or "kauf" in rec_text:
            rec_color = "green"
        elif "sell" in rec_text or "verkauf" in rec_text:
            rec_color = "red"

        qty_text = ""
        qty = item.get("recommended_quantity") or item.get("Empfohlene_Stueckzahl")
        if qty is not None:
            qty_text = f" ({qty} pcs.)"

        story.append(
            Paragraph(f"<b>Recommendation:</b> <font color='{rec_color}'>{rec}{qty_text}</font>", normal_style)
        )

        qty_reason = item.get("quantity_reasoning") or item.get("Grund_fuer_Menge")
        if qty_reason:
            story.append(Paragraph(f"<i>Strategy: {qty_reason}</i>", normal_style))

    story.append(Spacer(1, 6))

    reasoning = item.get("Reasoning") or item.get("Begründung") or item.get("Begruendung")
    if reasoning:
        story.append(Paragraph("AI Analysis & News Summary", header_style))
        text = str(reasoning).replace("\n", "<br/>")
        story.append(Paragraph(text, normal_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Data", header_style))
    exclude_fields = [
        "Reasoning", "Begründung", "Begruendung", "Recommendation", "Empfehlung",
        "Asset", "Ticker", "News", "RawNews",
        "Tiingo_Price", "Alpaca_Price", "Web_Price",
    ]
    data = []
    for k, v in item.items():
        if k not in exclude_fields and not isinstance(v, (dict, list)):
            val_str = str(v)
            if len(val_str) > 60:
                val_str = val_str[:60] + "..."
            data.append([k, val_str])

    current_price = None
    for key in ["Tiingo_Price", "Alpaca_Price", "Web_Price"]:
        if key in item and isinstance(item[key], dict):
            if "mid_price" in item[key]:
                current_price = item[key]["mid_price"]
                break
            if "price" in item[key]:
                current_price = item[key]["price"]
                break

    if current_price is not None:
        data.append(["Current Price", f"{current_price:.4f}"])

    if data:
        t = Table(data, colWidths=[1.5 * inch, 4 * inch])
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(t)

    doc.build(story)
