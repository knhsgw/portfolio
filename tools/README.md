# Updating the portfolio after the PDF changes

1. Replace `KanaHasegawaPortfolio.pdf` in the repo root with the new
   full-size export (keep the same filename). You don't need to make the
   compressed copy yourself — step 3 does it.

2. Set up the tool once:

   ```
   cd tools
   python -m venv .venv
   .venv/Scripts/pip install pymupdf pillow      # macOS/Linux: .venv/bin/pip
   ```

3. From the repo root, make the compressed PDF:

   ```
   tools/.venv/Scripts/python tools/compress_pdf.py     # macOS/Linux: tools/.venv/bin/python
   ```

   This overwrites `KanaHasegawaPortfolioCompressed.pdf` with a copy of
   the full-size PDF whose images are downsampled to 150 dpi and saved as
   JPEG (quality 60), giving roughly the same result as iLovePDF's
   "recommended" setting (~12 MB -> ~3 MB). Text is left as real text,
   which the next step relies on. Open the result and check a page or two
   still look sharp; if not, raise `QUALITY` or `DPI_TARGET` at the top
   of `compress_pdf.py` and run it again.

   Nothing on the site uses the compressed PDF at the moment: the
   Download button in `index.html` serves the full-size
   `KanaHasegawaPortfolio.pdf`. The compressed copy is kept as a smaller
   file to send around; point the button's `href` back at it if
   download size ever becomes a concern.

4. Then regenerate the gallery:

   ```
   tools/.venv/Scripts/python tools/update_gallery.py
   ```

   This regenerates `portfolio-images/` (WebP at 1000px and 2000px per
   page) and rewrites the gallery markup in `index.html` between the
   `GALLERY:START` / `GALLERY:END` comments. Everything else in
   `index.html` is left untouched.

   It renders from the full-size `KanaHasegawaPortfolio.pdf`, not the
   compressed one: the gallery's 2000px images need about 170 dpi and the
   compressed PDF only has 150, so photos looked soft. This costs about
   +10% on the 2000px images; the 1000px ones are unaffected. Add
   `--compressed` to render from the compressed PDF instead.

5. Manual follow-ups the script can't do for you:
   - If the hero section's look changed, re-screenshot `preview.jpg`
     (it's just a capture of the page top, used for link previews).
   - Bump `<lastmod>` in `sitemap.xml` to today's date.
   - Commit both PDFs, `index.html`, `portfolio-images/`, and `preview.jpg` if changed.

Page titles are read from each PDF page's own text layer and used for
filenames, alt text, and section headings — keep a text heading as the
first line of each page in the source document so this keeps working.
