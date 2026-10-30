"""Rebuild the five one-page PDFs from their editable Markdown sources.

Run: uv run python scripts/build_cheatsheets.py
Expected: five PDFs under output/pdf. Cost: $0; no AWS resources or network.
Render the PDFs with pdftoppm and inspect before publishing edited sheets.
"""

from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from common.config import ROOT


def footer(canvas, document):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#536879"))
    canvas.drawString(40, 25, "Nimbus Travel | Synthetic training data | docs/FEATURE_MAP.md")
    canvas.drawRightString(572, 25, str(document.page))


def main():
    styles = getSampleStyleSheet()
    for name, size, leading, color in (
        ("SheetTitle", 20, 23, "#123048"),
        ("SheetHeading", 10, 13, "#176b87"),
        ("SheetBody", 9, 12, "#202020"),
    ):
        styles.add(
            ParagraphStyle(
                name=name,
                fontName="Helvetica" if name == "SheetBody" else "Helvetica-Bold",
                fontSize=size,
                leading=leading,
                textColor=colors.HexColor(color),
                spaceAfter=5,
                spaceBefore=6 if name == "SheetHeading" else 0,
            )
        )
    directory = ROOT / "output/pdf"
    directory.mkdir(parents=True, exist_ok=True)
    for path in sorted((ROOT / "cheatsheets").glob("[0-9][0-9]_*.md")):
        blocks = path.read_text(encoding="utf-8").strip().split("\n\n")
        story = [Paragraph(escape(blocks[0][2:]), styles["SheetTitle"])]
        subtitle = blocks[1].split(". [Printable PDF]")[0]
        story += [
            Paragraph(escape(subtitle) + " | SDK 1.62 | 2026-10-29", styles["SheetBody"]),
            Spacer(1, 8),
        ]
        for block in blocks[2:]:
            if block.startswith("See [the feature map]"):
                continue
            heading = block.startswith("## ")
            text = block[3:] if heading else block
            story.append(
                Paragraph(
                    escape(text).replace("\n", "<br/>"),
                    styles["SheetHeading" if heading else "SheetBody"],
                )
            )
        target = directory / (path.stem + ".pdf")
        SimpleDocTemplate(
            str(target),
            pagesize=(612, 792),
            rightMargin=40,
            leftMargin=40,
            topMargin=35,
            bottomMargin=40,
        ).build(story, onFirstPage=footer, onLaterPages=footer)
        if len(PdfReader(target).pages) != 1:
            raise ValueError(f"Shorten {path.name}; its reference must fit one page")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
