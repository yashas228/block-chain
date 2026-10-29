"""Assemble the final project report DOCX."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import docx_kit as K           # noqa: E402
import build_report as A       # noqa: E402  front matter + chapters 1-3
import chapters_b as B         # noqa: E402  chapters 4-7, references, appendices

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "SP_FINAL_REPORT.docx")


def main():
    doc = K.build_document()
    K.add_header_footer(doc, "Blockchain-Based Academic Record Management and Verification System")

    A.title_page(doc)
    A.declaration(doc)
    A.certificate(doc)
    A.acknowledgement(doc)
    A.abstract(doc)
    A.contents(doc)

    A.chapter1(doc)
    A.chapter2(doc)
    A.chapter3(doc)
    B.chapter4(doc)
    B.chapter5(doc)
    B.chapter6(doc)
    B.chapter7(doc)
    B.references(doc)
    B.appendices(doc)

    props = doc.core_properties
    props.title = A.TITLE
    props.subject = A.SUBTITLE
    props.author = "; ".join(name for name, _ in A.STUDENTS)
    props.keywords = ("blockchain; academic records; verifiable credentials; Ethereum; "
                      "smart contracts; IPFS; student information system")
    props.comments = ("Final project report, ICFAI Foundation for Higher Education, Hyderabad, "
                      "October 2026.")

    K.enable_update_fields(doc)
    doc.save(OUT)
    print("wrote", OUT)
    return OUT


if __name__ == "__main__":
    main()
