#!/usr/bin/env python3
"""Generate a documentation fixture PDF with headings, body text, a table, and images."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _make_logo_png() -> bytes:
    img = Image.new("RGB", (240, 120), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((8, 8, 232, 112), radius=16, fill=(20, 184, 166))
    draw.text((28, 42), "Duckling", fill=(255, 255, 255))
    draw.text((28, 68), "Sample Asset", fill=(226, 232, 240))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_chart_png() -> bytes:
    img = Image.new("RGB", (320, 180), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 320, 180), fill=(248, 250, 252))
    bars = [40, 72, 55, 96, 68, 110, 84]
    for idx, height in enumerate(bars):
        x0 = 36 + idx * 36
        draw.rectangle((x0, 150 - height, x0 + 24, 150), fill=(14, 116, 144))
    draw.line((24, 150, 296, 150), fill=(100, 116, 139), width=2)
    draw.text((24, 12), "Quarterly Conversion Metrics", fill=(15, 23, 42))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def build_pdf(output: Path) -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        spaceAfter=12,
    )
    heading = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        spaceBefore=12,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15,
        spaceAfter=8,
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Duckling Sample Document",
        author="Duckling Docs",
    )

    logo_path = output.with_suffix(".logo.png")
    chart_path = output.with_suffix(".chart.png")
    logo_path.write_bytes(_make_logo_png())
    chart_path.write_bytes(_make_chart_png())

    table_data = [
        ["Region", "Documents", "Avg. Pages", "Success Rate"],
        ["North America", "1,245", "18.2", "98.4%"],
        ["Europe", "986", "16.7", "97.9%"],
        ["Asia Pacific", "1,102", "21.3", "98.1%"],
        ["Latin America", "437", "14.8", "96.8%"],
    ]
    table = Table(table_data, colWidths=[1.5 * inch, 1.2 * inch, 1.1 * inch, 1.1 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecfeff")]),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story = [
        Paragraph("Duckling Sample Document", title),
        Paragraph(
            "This fixture is used for documentation screenshots. It includes headings, body text, "
            "an embedded logo, a chart image, and a structured table so export previews and "
            "extraction tabs render realistic content.",
            body,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Product Overview", heading),
        Paragraph(
            "Duckling converts PDFs and office documents into Markdown, HTML, JSON, and other "
            "formats while preserving tables, images, and layout structure.",
            body,
        ),
        RLImage(str(logo_path), width=2.4 * inch, height=1.2 * inch),
        Spacer(1, 0.1 * inch),
        Paragraph("Regional Processing Summary", heading),
        table,
        Spacer(1, 0.15 * inch),
        Paragraph("Performance Chart", heading),
        RLImage(str(chart_path), width=4.5 * inch, height=2.5 * inch),
        Spacer(1, 0.1 * inch),
        Paragraph(
            "Use this document when regenerating screenshots so image galleries, table downloads, "
            "and preview panes show meaningful extracted content in every locale.",
            body,
        ),
    ]

    doc.build(story)
    logo_path.unlink(missing_ok=True)
    chart_path.unlink(missing_ok=True)


def main() -> None:
    out = Path(__file__).with_name("sample-document.pdf")
    build_pdf(out)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
