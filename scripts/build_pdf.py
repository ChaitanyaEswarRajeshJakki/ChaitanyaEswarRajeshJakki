#!/usr/bin/env python3
"""
Build a dated resume PDF from scripts/resume_data.json.

Output file: <repo-root>/Jakki_Chaitanya_Eswar_Rajesh_<DD-MM-YY>.pdf
Previous dated PDFs are NOT deleted — kept as history.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

ROOT        = Path(__file__).resolve().parent.parent
RESUME_DATA = ROOT / "scripts" / "resume_data.json"

def dated_output():
    today = datetime.now(timezone.utc).strftime("%d-%m-%y")
    return ROOT / f"Jakki_Chaitanya_Eswar_Rajesh_{today}.pdf"


# ─── Styles ───────────────────────────────────────────────────────────────────
def make_styles():
    B, I = "Helvetica-Bold", "Helvetica-Oblique"
    R    = "Helvetica"
    return {
        "name":    ParagraphStyle("name",    fontName=B, fontSize=15, leading=18,
                                  alignment=TA_CENTER, spaceAfter=2),
        "title":   ParagraphStyle("title",   fontName=R, fontSize=10, leading=13,
                                  alignment=TA_CENTER, spaceAfter=2),
        "contact": ParagraphStyle("contact", fontName=R, fontSize=9,  leading=12,
                                  alignment=TA_CENTER, spaceAfter=4,
                                  textColor=colors.HexColor("#333333")),
        "section": ParagraphStyle("section", fontName=B, fontSize=10, leading=13,
                                  spaceBefore=6, spaceAfter=2),
        "body":    ParagraphStyle("body",    fontName=R, fontSize=9,  leading=12,
                                  spaceAfter=1),
        "bullet":  ParagraphStyle("bullet",  fontName=R, fontSize=9,  leading=12,
                                  spaceAfter=1, leftIndent=12, firstLineIndent=-6),
        "subhead": ParagraphStyle("subhead", fontName=B, fontSize=9,  leading=13,
                                  spaceAfter=1, spaceBefore=4),
        "proj":    ParagraphStyle("proj",    fontName=B, fontSize=9,  leading=13,
                                  spaceAfter=1, spaceBefore=5),
        "italic":  ParagraphStyle("italic",  fontName=I, fontSize=8.5, leading=12,
                                  spaceAfter=2, textColor=colors.HexColor("#555555")),
    }

def hr():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor("#888888"),
                      spaceAfter=4, spaceBefore=2)

def section(text, s):
    # Plain bold uppercase header — no decorative glyph, so ATS text extraction
    # reads clean section names (the old &#9632; / ■ marker garbled parsing).
    return Paragraph(text, s["section"])

def bullet(text, s):
    return Paragraph(f"• {text}", s["bullet"])

def body(text, s):
    return Paragraph(text, s["body"])


# ─── Build ────────────────────────────────────────────────────────────────────
def build(output_path=None):
    data = json.loads(RESUME_DATA.read_text(encoding="utf-8"))
    out  = Path(output_path) if output_path else dated_output()
    s    = make_styles()

    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.1*cm,  bottomMargin=1.1*cm,
    )
    story = []
    h = data["header"]

    # ── Header ────────────────────────────────────────────────────────────────
    story += [
        Paragraph(h["name"], s["name"]),
        Paragraph(h["title"], s["title"]),
        Paragraph(f'{h["phone"]}  |  {h["email"]}  |  {h["location"]}', s["contact"]),
        Paragraph(h["links"], s["contact"]),
        hr(),
    ]

    # ── Summary ───────────────────────────────────────────────────────────────
    story += [section("PROFESSIONAL SUMMARY", s), body(data["summary"], s), hr()]

    # ── Skills ────────────────────────────────────────────────────────────────
    story.append(section("TECHNICAL SKILLS", s))
    for label, val in data["skills"].items():
        story.append(body(f"<b>{label}:</b> {val}", s))
    story.append(hr())

    # ── Experience ────────────────────────────────────────────────────────────
    story.append(section("PROFESSIONAL EXPERIENCE", s))
    for exp in data["experience"]:
        story += [
            Paragraph(
                f'<b>{exp["title"]}</b>  |  {exp["company"]}  |  {exp["location"]}',
                s["subhead"]),
            body(f'{exp["period"]}  |  IT Experience: {exp["it_experience"]}', s),
            Spacer(1, 4),
        ]
        for sec in exp["sections"]:
            story.append(Paragraph(f'<b>{sec["heading"]}</b>', s["subhead"]))
            story += [bullet(b, s) for b in sec["bullets"]]
    story.append(hr())

    # ── Prior history ─────────────────────────────────────────────────────────
    ph = data["prior_history"]
    story += [
        section("CAREER TRANSITION & PRIOR WORK HISTORY", s),
        Paragraph(f'<i>{ph["intro"]}</i>', s["italic"]),
    ]
    for role in ph["roles"]:
        parts = [f'<b>{role["title"]}</b>']
        if "company" in role:
            parts.append(role["company"])
        if "location" in role:
            parts.append(role["location"])
        parts.append(role["period"])
        story.append(Paragraph("  |  ".join(parts), s["subhead"]))
        if "note" in role:
            story.append(body(role["note"], s))
        story += [bullet(b, s) for b in role["bullets"]]
    story.append(hr())

    # ── Projects ──────────────────────────────────────────────────────────────
    story.append(section("KEY PROJECTS", s))
    for proj in data["projects"]:
        block = [
            Paragraph(
                f'<b>{proj["name"]} — {proj["subtitle"]}</b>  |  '
                f'{proj["stack"]}  |  {proj["year"]}',
                s["proj"]),
        ] + [bullet(b, s) for b in proj["bullets"]]
        story.append(KeepTogether(block))
    story.append(hr())

    # ── Education ─────────────────────────────────────────────────────────────
    story.append(section("EDUCATION & CERTIFICATIONS", s))
    for edu in data["education"]:
        story.append(bullet(edu, s))
    story.append(hr())

    # ── Government clients ────────────────────────────────────────────────────
    story.append(section("GOVERNMENT CLIENT ENGAGEMENTS (VIA WEST ADVANCED TECHNOLOGIES)", s))
    for client in data["government_clients"]:
        story.append(bullet(client, s))

    doc.build(story)
    print(f"PDF saved: {out}")
    return str(out)


if __name__ == "__main__":
    build()
