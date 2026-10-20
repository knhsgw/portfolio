"""Regenerate the portfolio gallery from KanaHasegawaPortfolio.pdf.

Run this after replacing the PDF (see tools/README.md for the full
process). It renders from the full-size PDF because the compressed one
is only 150 dpi, which looks soft at the 2000px gallery size; pass
--compressed to use KanaHasegawaPortfolioCompressed.pdf instead:

    python -m venv tools/.venv
    tools/.venv/Scripts/pip install pymupdf pillow      (or tools/.venv/bin/pip on macOS/Linux)
    tools/.venv/Scripts/python tools/update_gallery.py

What it does:
  1. Renders every PDF page to WebP at 1000px and 2000px wide into
     portfolio-images/ (old files are wiped first).
  2. Regenerates preview.jpg (the og:image link-preview card) from
     a fresh screenshot-style crop is NOT done here — preview.jpg is a
     screenshot of the live page hero, see README note below.
  3. Rewrites the gallery markup between the
     <!-- GALLERY:START --> / <!-- GALLERY:END --> markers in index.html.

Page titles (used for filenames and alt text) are read from each PDF
page's own text layer, so keep a text heading as the first line of
each page in the source document.

If the number of pages, their order, or their titles change, this
script's regenerated markup reflects that automatically. If you are
only swapping in updated artwork for the *same* pages with the *same*
titles, the output filenames will be identical and this is still safe
to re-run.
"""
import argparse
import html
import io
import json
import re
import unicodedata
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "KanaHasegawaPortfolio.pdf"
COMPRESSED_PDF = ROOT / "KanaHasegawaPortfolioCompressed.pdf"
OUT = ROOT / "portfolio-images"
INDEX = ROOT / "index.html"
WIDTHS = [1000, 2000]
QUALITY = 82

# Only the "GALLERY:START" part is matched, so the rest of the comment
# (e.g. the dash, which editors have mangled before) can change freely.
START_MARKER = re.compile(r"<!-- GALLERY:START.*?-->")
END_MARKER = "<!-- GALLERY:END -->"


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text)


def page_title(page, index):
    lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
    if not lines:
        return f"Portfolio page {index}"
    return lines[0] if index > 1 else "Kana Hasegawa - Creative Pattern Cutter"


def render(page, width):
    zoom = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def export_images(pdf=PDF, out=OUT):
    out.mkdir(exist_ok=True)
    for stale in out.glob("*.webp"):
        stale.unlink()

    doc = fitz.open(pdf)
    manifest = []
    total = doc.page_count

    for i, page in enumerate(doc, start=1):
        title = page_title(page, i)
        slug = f"{i:02d}-{slugify(title)}"
        largest = render(page, max(WIDTHS))

        for w in WIDTHS:
            img = largest if w == max(WIDTHS) else largest.resize(
                (w, round(largest.height * w / largest.width)), Image.LANCZOS
            )
            img.save(out / f"{slug}-{w}.webp", "WEBP", quality=QUALITY, method=6)

        manifest.append({
            "slug": slug, "title": title, "page": i, "total": total,
            "width": WIDTHS[-1], "height": largest.height,
        })

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"exported {total} pages from {pdf.name} -> {out}")
    return manifest


def figure(p, total, first):
    slug, t = p["slug"], p["title"]
    alt = (f"{t}, portfolio page {p['page']} of {total}" if p["page"] > 1
           else "Kana Hasegawa portfolio title page, creative pattern cutter")
    loading_attrs = 'loading="eager"\n                         fetchpriority="high"' if first \
        else 'loading="lazy"\n                         decoding="async"'
    return f'''                <figure class="page">
                    <img src="portfolio-images/{slug}-1000.webp"
                         srcset="portfolio-images/{slug}-1000.webp 1000w, portfolio-images/{slug}-2000.webp 2000w"
                         sizes="(max-width: 2000px) 100vw, 2000px"
                         width="{p['width']}" height="{p['height']}"
                         alt="{html.escape(alt, quote=True)}"
                         {loading_attrs}>
                </figure>'''


def build_gallery_html(manifest):
    total = manifest[0]["total"]
    return "\n".join(
        figure(p, total, first=(p["page"] == 1)) for p in manifest
    )


def splice_into_index(gallery_html):
    src = INDEX.read_text(encoding="utf-8")
    start_match = START_MARKER.search(src)
    if not start_match or END_MARKER not in src:
        raise SystemExit(
            "GALLERY:START/END markers not found in index.html — "
            "the gallery section may have been edited by hand. Aborting."
        )
    start = start_match.end()
    end = src.index(END_MARKER)
    new_src = src[:start] + "\n" + gallery_html + "\n        " + src[end:]
    INDEX.write_text(new_src, encoding="utf-8")
    print(f"updated gallery markup in {INDEX}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compressed", action="store_true",
                        help=f"render from {COMPRESSED_PDF.name} instead of {PDF.name}")
    args = parser.parse_args()

    manifest = export_images(COMPRESSED_PDF if args.compressed else PDF)
    gallery_html = build_gallery_html(manifest)
    splice_into_index(gallery_html)
    print(
        "\nDone. Remaining manual steps:\n"
        "  1. Preview the site locally and re-screenshot preview.jpg (the hero section)\n"
        "     if the hero itself changed - otherwise it can stay as-is.\n"
        "  2. Bump <lastmod> in sitemap.xml to today's date.\n"
        "  3. Commit both PDFs, index.html, portfolio-images/, and preview.jpg (if changed)."
    )


if __name__ == "__main__":
    main()
