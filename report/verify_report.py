"""Structural checks on the generated report."""
import os
import re
import zipfile

from docx import Document

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "SP_FINAL_REPORT.docx")

doc = Document(PATH)

paras = doc.paragraphs
text_all = "\n".join(p.text for p in paras)
words = len(re.findall(r"\b[\w'-]+\b", text_all))

print("paragraphs:", len(paras))
print("tables:", len(doc.tables))
print("images:", len(doc.inline_shapes))
print("body words (excluding tables):", words)
print("table cells:", sum(len(t.rows) * len(t.columns) for t in doc.tables))

heads = [(p.style.name, p.text) for p in paras if p.style.name.startswith("Heading")]
print("headings: H1=%d H2=%d H3=%d" % (
    sum(1 for s, _ in heads if s == "Heading 1"),
    sum(1 for s, _ in heads if s == "Heading 2"),
    sum(1 for s, _ in heads if s == "Heading 3")))
print("front-matter headings:", [t for s, t in heads if s == "FrontHeading"])

figs = [p.text for p in paras if p.style.name == "FigCaption"]
tabs = [p.text for p in paras if p.style.name == "TabCaption"]
print("\nfigure captions:", len(figs))
for c in figs:
    print("  ", c[:96])
print("table captions:", len(tabs))
for c in tabs:
    print("  ", c[:96])

sec = doc.sections[0]
usable = (sec.page_width - sec.left_margin - sec.right_margin) / 914400
over = []
for i, t in enumerate(doc.tables, 1):
    total = sum((c.width.inches if c.width else 0) for c in t.rows[0].cells)
    if total > usable + 0.01:
        over.append((i, round(total, 2)))
print("\nusable width in:", round(usable, 2), "| tables too wide:", over)
print("image widths in:", sorted({round(s.width.inches, 2) for s in doc.inline_shapes}))

refs = sorted(set(re.findall(r"Sections? (\d+\.\d+(?:\.\d+)?)", text_all)))
nums = {re.match(r"(\d+(?:\.\d+)*)\.?\s", t).group(1)
        for s, t in heads if s.startswith("Heading") and re.match(r"\d", t)}
print("section refs:", refs)
print("dangling section refs:", [r for r in refs if r not in nums])
fig_refs = sorted(set(re.findall(r"Figure (\d+\.\d+)", text_all)))
print("figure refs:", fig_refs)

leftovers = {
    "markdown bold": text_all.count("**"),
    "markdown backtick": text_all.count("`"),
    "literal None": len(re.findall(r"\bNone\b", text_all)),
    "double space before period": len(re.findall(r"\s\.", text_all)),
}
print("leftover artefacts:", leftovers)

with zipfile.ZipFile(PATH) as z:
    xml = z.read("word/document.xml").decode("utf-8")
    settings = z.read("word/settings.xml").decode("utf-8")
    names = z.namelist()
print("embedded pictures in xml:", xml.count("<pic:pic"))
print("media files:", len([n for n in names if n.startswith("word/media/")]))
print("updateFields:", "updateFields" in settings)
print("TOC field present:", "TOC \\o" in xml)
print("List of figures field:", "FigCaption,1" in xml)
print("List of tables field:", "TabCaption,1" in xml)
print("file size (KB):", round(os.path.getsize(PATH) / 1024, 1))
