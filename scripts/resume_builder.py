#!/usr/bin/env python3
"""
resume_builder.py — Generate a formatted .docx resume from structured text.

Usage:
    python3 scripts/resume_builder.py --input resume_draft.txt --output resumes/Company_Role_Resume_2026-01-01.docx

The input file should be the Claude-generated resume text draft.
This script applies consistent formatting per the project's typography spec.

Typography Spec:
    - Body/content text: 10pt (sz=20) Calibri, black
    - Name: 17pt (sz=34) Calibri Bold
    - Contact line: 9.5pt (sz=19) Calibri
    - Section headers: 10pt (sz=20) Calibri Bold, small caps, border-bottom
    - Bullet items: 10pt (sz=20) Calibri, indent left=360 hanging=180
    - Line spacing: atLeast 244 (12.2pt)
    - Page margins: top/bottom=0.5in, left/right=0.6in
"""

import argparse
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("ERROR: python-docx is not installed.")
    print("Run: pip3 install python-docx --break-system-packages")
    sys.exit(1)


BLACK = RGBColor(0x00, 0x00, 0x00)
FONT = "Calibri"


def set_line_spacing(paragraph, line=244, before=0, after=0):
    pf = paragraph._p.get_or_add_pPr()
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:line"), str(line))
    spacing.set(qn("w:lineRule"), "atLeast")
    spacing.set(qn("w:before"), str(before))
    spacing.set(qn("w:after"), str(after))
    pf.append(spacing)


def add_run(paragraph, text, size=20, bold=False, italic=False, color=BLACK):
    run = paragraph.add_run(text)
    run.font.name = FONT
    run.font.size = Pt(size / 2)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return run


def add_name(doc, name):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_line_spacing(p, before=0, after=0)
    add_run(p, name, size=34, bold=True)
    return p


def add_contact_line(doc, contact_text):
    """contact_text: e.g. 'City, ST  |  phone  |  email  |  LinkedIn'"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_line_spacing(p, before=0, after=0)
    add_run(p, contact_text, size=19)
    return p


def add_section_header(doc, title):
    p = doc.add_paragraph()
    set_line_spacing(p, before=80, after=0)
    run = add_run(p, title.upper(), size=20, bold=True)
    run.font.all_caps = True
    # Bottom border
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    p._p.get_or_add_pPr().append(pBdr)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph()
    set_line_spacing(p)
    # Indent
    pPr = p._p.get_or_add_pPr()
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "360")
    ind.set(qn("w:hanging"), "180")
    pPr.append(ind)
    add_run(p, "•  " + text, size=20)
    return p


def add_role_header(doc, company, title, location, dates):
    """Two-column-style role header: Bold Company + Title left, Dates right."""
    p = doc.add_paragraph()
    set_line_spacing(p, before=60, after=0)
    add_run(p, company, size=20, bold=True)
    add_run(p, " — ", size=20)
    add_run(p, title, size=20, bold=True)

    # Right-align dates using a tab stop (simplified: just append)
    add_run(p, f"  {location}  |  {dates}", size=18, italic=True)
    return p


def set_margins(doc, top=0.5, bottom=0.5, left=0.6, right=0.6):
    section = doc.sections[0]
    section.top_margin = Inches(top)
    section.bottom_margin = Inches(bottom)
    section.left_margin = Inches(left)
    section.right_margin = Inches(right)


def build_resume(input_path: Path, output_path: Path):
    """
    Basic builder — reads a plain text draft and creates a formatted .docx.
    For fully custom formatting, edit this function to match your resume structure.
    """
    doc = Document()
    set_margins(doc)

    # Remove default paragraph spacing
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(10)

    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            i += 1
            continue

        # Detect section headers (all caps lines or lines starting with ##)
        if line.startswith("## ") or (line.isupper() and len(line) > 3):
            add_section_header(doc, line.lstrip("# ").strip())

        # Bullet points
        elif line.startswith("- ") or line.startswith("• "):
            add_bullet(doc, line.lstrip("-• ").strip())

        # Default: body paragraph
        else:
            p = doc.add_paragraph()
            set_line_spacing(p)
            add_run(p, line)

        i += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Build a formatted resume .docx from a text draft.")
    parser.add_argument("--input", required=True, help="Path to plain text resume draft")
    parser.add_argument("--output", required=True, help="Output .docx path (e.g., resumes/Acme_Analyst_Resume_2026-01-01.docx)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    build_resume(input_path, output_path)


if __name__ == "__main__":
    main()
