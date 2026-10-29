"""Check that OOXML property children appear in schema order."""
import os
import zipfile
from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "SP_FINAL_REPORT.docx")

PPR = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
       "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
       "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
       "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing",
       "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment",
       "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]

TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
         "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
         "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"]

TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap",
        "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"]

TRPR = ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit",
        "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden"]

SETTINGS = ["writeProtection", "view", "zoom", "removePersonalInformation",
            "removeDateAndTime", "doNotDisplayPageBoundaries", "displayBackgroundShape",
            "printPostScriptOverText", "printFractionalCharacterWidth", "printFormsData",
            "embedTrueTypeFonts", "embedSystemFonts", "saveSubsetFonts", "saveFormsData",
            "mirrorMargins", "alignBordersAndEdges", "bordersDoNotSurroundHeader",
            "bordersDoNotSurroundFooter", "gutterAtTop", "hideSpellingErrors",
            "hideGrammaticalErrors", "activeWritingStyle", "proofState", "formsDesign",
            "attachedTemplate", "linkStyles", "stylePaneFormatFilter", "stylePaneSortMethod",
            "documentType", "mailMerge", "revisionView", "trackChanges", "doNotTrackMoves",
            "doNotTrackFormatting", "documentProtection", "autoFormatOverride",
            "styleLockTheme", "styleLockQFSet", "defaultTabStop", "autoHyphenation",
            "consecutiveHyphenLimit", "hyphenationZone", "doNotHyphenateCaps",
            "showEnvelope", "summaryLength", "clickAndTypeStyle", "defaultTableStyle",
            "evenAndOddHeaders", "bookFoldRevPrinting", "bookFoldPrinting",
            "bookFoldPrintingSheets", "drawingGridHorizontalSpacing",
            "drawingGridVerticalSpacing", "displayHorizontalDrawingGridEvery",
            "displayVerticalDrawingGridEvery", "doNotUseMarginsForDrawingGridOrigin",
            "drawingGridHorizontalOrigin", "drawingGridVerticalOrigin",
            "doNotShadeFormData", "noPunctuationKerning", "characterSpacingControl",
            "printTwoOnOne", "strictFirstAndLastChars", "noLineBreaksAfter",
            "noLineBreaksBefore", "savePreviewPicture", "doNotValidateAgainstSchema",
            "saveInvalidXml", "ignoreMixedContent", "alwaysShowPlaceholderText",
            "doNotDemarcateInvalidXml", "saveXmlDataOnly", "useXSLTWhenSaving",
            "saveThroughXslt", "showXMLTags", "alwaysMergeEmptyNamespace", "updateFields",
            "hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids",
            "mathPr", "uiCompat97To2003", "attachedSchema", "themeFontLang",
            "clrSchemeMapping", "doNotIncludeSubdocsInStats", "doNotAutoCompressPictures",
            "forceUpgrade", "captions", "readModeInkLockDown", "smartTagType",
            "schemaLibrary", "shapeDefaults", "doNotEmbedSmartTags", "decimalSymbol",
            "listSeparator"]

problems = []

with zipfile.ZipFile(PATH) as z:
    parts = {
        "document.xml": z.read("word/document.xml"),
        "settings.xml": z.read("word/settings.xml"),
        "header1.xml": z.read("word/header1.xml") if "word/header1.xml" in z.namelist() else None,
        "footer1.xml": z.read("word/footer1.xml") if "word/footer1.xml" in z.namelist() else None,
        "styles.xml": z.read("word/styles.xml"),
    }

for name, data in parts.items():
    if data is None:
        continue
    root = etree.fromstring(data)
    for tag, order in (("pPr", PPR), ("tblPr", TBLPR), ("tcPr", TCPR), ("trPr", TRPR),
                       ("settings", SETTINGS), ("rPr", None)):
        if order is None:
            continue
        for el in root.iter(W + tag):
            seen = []
            for child in el:
                local = etree.QName(child).localname
                if local in order:
                    seen.append((order.index(local), local))
            indexes = [i for i, _ in seen]
            if indexes != sorted(indexes):
                problems.append((name, tag, [n for _, n in seen]))

print("out-of-order property blocks:", len(problems))
for item in problems[:10]:
    print("  ", item)

# duplicate single-value children
dups = 0
for name, data in parts.items():
    if data is None:
        continue
    root = etree.fromstring(data)
    for el in root.iter(W + "pPr"):
        names = [etree.QName(c).localname for c in el]
        if len(names) != len(set(names)):
            dups += 1
print("pPr blocks with duplicate children:", dups)

# every drawing has a caption after it
doc = etree.fromstring(parts["document.xml"])
body = doc.find(W + "body")
seq = [etree.QName(c).localname for c in body]
print("body children:", len(seq))
print("paragraphs:", seq.count("p"), "tables:", seq.count("tbl"))
