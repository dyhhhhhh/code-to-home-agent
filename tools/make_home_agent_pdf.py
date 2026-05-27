from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "home-agent-whitepaper.md"
TARGET = ROOT / "docs" / "home-agent-whitepaper.pdf"
FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_NAME = "MicrosoftYaHei"


def register_font() -> None:
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def clean_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font name=\"Courier\">\1</font>", text)
    return text


def make_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCN",
            parent=styles["Title"],
            fontName=FONT_NAME,
            fontSize=24,
            leading=32,
            spaceAfter=12,
            textColor=colors.HexColor("#102033"),
        ),
        "h2": ParagraphStyle(
            "H2CN",
            parent=styles["Heading1"],
            fontName=FONT_NAME,
            fontSize=17,
            leading=24,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#12395c"),
        ),
        "h3": ParagraphStyle(
            "H3CN",
            parent=styles["Heading2"],
            fontName=FONT_NAME,
            fontSize=13,
            leading=20,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#1d4d74"),
        ),
        "body": ParagraphStyle(
            "BodyCN",
            parent=styles["BodyText"],
            fontName=FONT_NAME,
            fontSize=10.5,
            leading=17,
            spaceAfter=6,
            firstLineIndent=0,
        ),
        "bullet": ParagraphStyle(
            "BulletCN",
            parent=styles["BodyText"],
            fontName=FONT_NAME,
            fontSize=10.5,
            leading=17,
            leftIndent=14,
            firstLineIndent=-8,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "QuoteCN",
            parent=styles["BodyText"],
            fontName=FONT_NAME,
            fontSize=11,
            leading=18,
            leftIndent=10,
            rightIndent=10,
            textColor=colors.HexColor("#334155"),
            backColor=colors.HexColor("#eef6fb"),
            borderPadding=8,
            spaceBefore=6,
            spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "CodeCN",
            fontName="Courier",
            fontSize=8.5,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            backColor=colors.HexColor("#f3f6f8"),
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
        ),
    }


def parse_table(lines: list[str], index: int):
    table_lines = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        table_lines.append(lines[index].strip())
        index += 1
    rows = []
    for n, line in enumerate(table_lines):
        cells = [clean_inline(c.strip()) for c in line.strip("|").split("|")]
        if n == 1 and all(set(c.replace(":", "").replace("-", "")) == set() for c in cells):
            continue
        rows.append(cells)
    return rows, index


def build_story() -> list:
    styles = make_styles()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story: list = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line:
            i += 1
            continue

        if line.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            story.append(Preformatted("\n".join(block), styles["code"]))
            continue

        if line.startswith("|"):
            rows, i = parse_table(lines, i)
            if rows:
                table = Table(rows, repeatRows=1, hAlign="LEFT")
                table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                            ("LEADING", (0, 0), (-1, -1), 11),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 8))
            continue

        if line.startswith("# "):
            story.append(Paragraph(clean_inline(line[2:]), styles["title"]))
            story.append(Spacer(1, 6))
        elif line.startswith("## "):
            if story:
                story.append(Spacer(1, 4))
            story.append(Paragraph(clean_inline(line[3:]), styles["h2"]))
        elif line.startswith("### "):
            story.append(Paragraph(clean_inline(line[4:]), styles["h3"]))
        elif line.startswith("> "):
            story.append(Paragraph(clean_inline(line[2:]), styles["quote"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + clean_inline(line[2:]), styles["bullet"]))
        else:
            story.append(Paragraph(clean_inline(line), styles["body"]))
        i += 1

    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(200 * mm, 10 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


def main() -> None:
    register_font()
    doc = SimpleDocTemplate(
        str(TARGET),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Home Agent 家庭智能体白皮书",
        author="code-to-home-agent",
    )
    story = build_story()
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(TARGET)


if __name__ == "__main__":
    main()

