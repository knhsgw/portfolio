# Updating the portfolio after the PDF changes

1. Replace `KanaHasegawaPortfolio.pdf` and `KanaHasegawaPortfolioCompressed.pdf`
   in the repo root with the new versions (keep the same filenames).

2. Set up the tool once:

   ```
   cd tools
   python -m venv .venv
   .venv/Scripts/pip install pymupdf pillow      # macOS/Linux: .venv/bin/pip
   ```

3. Run it from the repo root:

   ```
   tools/.venv/Scripts/python tools/update_gallery.py   # macOS/Linux: tools/.venv/bin/python
   ```

   This regenerates `portfolio-images/` (WebP at 1000px and 2000px per
   page) and rewrites the gallery markup in `index.html` between the
   `GALLERY:START` / `GALLERY:END` comments. Everything else in
   `index.html` is left untouched.

4. Manual follow-ups the script can't do for you:
   - If the hero section's look changed, re-screenshot `preview.jpg`
     (it's just a capture of the page top, used for link previews).
   - Bump `<lastmod>` in `sitemap.xml` to today's date.
   - Commit `index.html`, `portfolio-images/`, and `preview.jpg` if changed.

Page titles are read from each PDF page's own text layer and used for
filenames, alt text, and section headings — keep a text heading as the
first line of each page in the source document so this keeps working.
