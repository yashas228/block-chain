# Final report source

The final project report (`SP_FINAL_REPORT.docx`, repository root) is generated from these
scripts so that it can be rebuilt after any change to the project.

| File | Purpose |
|---|---|
| `make_report.py` | Entry point: assembles the document and writes `SP_FINAL_REPORT.docx` |
| `build_report.py` | Title page, front matter, Chapters 1–3 |
| `chapters_b.py` | Chapters 4–7, references and appendices |
| `docx_kit.py` | Styles, captions, tables, fields (TOC, page numbers) |
| `make_figures.py` | Draws all diagrams and result charts into `report/figures/` |
| `verify_report.py` | Prints structural checks (word count, headings, widths, fields) |
| `check_order.py` | Validates OOXML child ordering so Word opens the file cleanly |

## Rebuild

```bash
python -m pip install python-docx matplotlib
python report/make_figures.py      # figures -> report/figures/*.png
python report/make_report.py       # report  -> SP_FINAL_REPORT.docx
python report/verify_report.py     # sanity checks
```

## After opening in Word

The document sets `updateFields`, so Word refreshes the table of contents, list of figures and
list of tables when the file is opened (accept the prompt if it appears). If a list still shows
placeholder text, right-click it and choose **Update Field**.

Measured values in Chapter 6 are read from `docs/measurements.json`; re-running
`node scripts/measure.js` and rebuilding regenerates the charts with the new numbers, but the
tables in `chapters_b.py` are written out and must be updated by hand if the measurements change.
