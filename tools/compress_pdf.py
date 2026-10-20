"""Make KanaHasegawaPortfolioCompressed.pdf from KanaHasegawaPortfolio.pdf.

Run this after replacing the full-size PDF, before update_gallery.py:

    tools/.venv/Scripts/python tools/compress_pdf.py

Every raster image is downsampled to 150 dpi (at the size it is drawn
on the page) and re-encoded as JPEG, matching the iLovePDF output the
site used previously. Text and vector content are left alone, so page
titles stay readable for update_gallery.py.
"""
import io
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "KanaHasegawaPortfolio.pdf"
DST = ROOT / "KanaHasegawaPortfolioCompressed.pdf"
DPI_TARGET = 150
QUALITY = 60


def compress_image(doc, page, xref):
    rects = page.get_image_rects(xref)
    if not rects:
        return
    # largest on-page size wins, so a reused image never ends up too small
    shown_w = max(r.width for r in rects) / 72
    shown_h = max(r.height for r in rects) / 72
    info = doc.extract_image(xref)
    w = round(shown_w * DPI_TARGET)
    h = round(shown_h * DPI_TARGET)
    if w >= info["width"] or h >= info["height"]:
        return

    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha or pix.colorspace is None or pix.colorspace.n not in (1, 3):
        return  # leave masks, CMYK and transparent images as they are
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    img = img.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=QUALITY, optimize=True)
    if len(buf.getvalue()) < len(info["image"]):
        page.replace_image(xref, stream=buf.getvalue())


def main():
    doc = pymupdf.open(SRC)
    done = set()
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref not in done:
                done.add(xref)
                compress_image(doc, page, xref)
    doc.save(DST, garbage=4, deflate=True, clean=True)

    before, after = SRC.stat().st_size, DST.stat().st_size
    print(f"{SRC.name}: {before / 1e6:.1f} MB -> {DST.name}: {after / 1e6:.1f} MB "
          f"({doc.page_count} pages)")


if __name__ == "__main__":
    main()
