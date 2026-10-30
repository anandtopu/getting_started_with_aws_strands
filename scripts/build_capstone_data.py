"""Generate two synthetic invoice images and labels. Run: uv run python
scripts/build_capstone_data.py.

Expected: two invoices; local cost $0, no AWS resources. No existing receipt is edited."""

import json

from PIL import Image, ImageDraw, ImageFont

from common.config import ROOT


def main():
    folder = ROOT / "capstones/03_document_intelligence/fixtures"
    (folder / "invoices").mkdir(parents=True, exist_ok=True)
    rows = []
    for number, total in [(1, 11000), (2, 12500)]:
        row = {
            "invoice_id": f"INV-{number:03}",
            "file": f"invoices/invoice_{number:02}.png",
            "subtotal_cents": 10000,
            "tax_cents": 1000,
            "total_cents": total,
            "anomaly": None if number == 1 else "total_mismatch",
        }
        canvas = Image.new("RGB", (800, 500), "white")
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default(size=25)
        lines = [
            "NIMBUS TRAVEL - SYNTHETIC INVOICE",
            row["invoice_id"],
            "Transfer service: USD 100.00",
            "Subtotal: USD 100.00",
            "Tax: USD 10.00",
            f"Total: USD {total / 100:.2f}",
            "Training fixture - not payable",
        ]
        for index, line in enumerate(lines):
            draw.text((35, 35 + index * 58), line, fill="#123048", font=font)
        canvas.save(folder / row["file"])
        rows.append(row)
    (folder / "invoices.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    print("Wrote two synthetic invoices and labels.")


if __name__ == "__main__":
    main()
