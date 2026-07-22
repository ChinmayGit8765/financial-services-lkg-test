#!/usr/bin/env python3
"""
Render the LKG Portfolio Sector Digest to .docx and re-enforce the flag gate.

The agent nominates flags; this script is the deterministic gate. Any flag
missing a required field or carrying an out-of-enum value is demoted to the
Watchlist with the failure named — it never renders as a flag.

Usage: python build_digest.py digest.json [output.docx]
Requires: python-docx  (pip install python-docx)
"""
import json
import re
import sys
from pathlib import Path

REQUIRED = ["headline", "source_url", "polarity", "mechanism",
            "implication", "owner", "severity"]
HEADLINE_MAX = 140  # the schema's "one line", made checkable
MECHANISMS = {  # the frozen taxonomy from references/sectors/ — no extensions mid-run
    "housing-turnover", "rates-sentiment", "input-costs", "seasonality",
    "franchise-risk", "ma-distress", "competitor-move",
}
ENUMS = {
    "polarity": {"risk", "opportunity", "watch"},
    "owner": {"GM", "board", "QLC"},
    "severity": {"low", "med", "high"},
    "mechanism": MECHANISMS,
}
SEV_ORDER = {"high": 0, "med": 1, "low": 2}
OWNER_ORDER = {"board": 0, "QLC": 1, "GM": 2}

PRIMARY_LABELS = {  # originators get clean names; everything else shows its bare domain
    "cotality.com.au": "Cotality", "abs.gov.au": "ABS", "accc.gov.au": "ACCC",
    "westpaciq.com.au": "Westpac IQ", "rba.gov.au": "RBA", "asx.com.au": "ASX",
}
NUM_RE = re.compile(r"([+\-]?\$?\d[\d,.]*(?:%|bp|bn|m\b)?)")


def gate(flags):
    """Split nominated flags into (passed, demoted-with-reason)."""
    passed, demoted = [], []
    for f in flags:
        missing = [k for k in REQUIRED if not str(f.get(k, "")).strip()]
        bad = [k for k, allowed in ENUMS.items()
               if f.get(k) and f[k] not in allowed]
        head = str(f.get("headline", "")).strip()
        over = len(head) > HEADLINE_MAX
        multiline = "\n" in head
        if missing or bad or over or multiline:
            reason = "failed gate: " + "; ".join(
                (["missing " + ", ".join(missing)] if missing else []) +
                [f"invalid {k}={f[k]!r}" for k in bad] +
                ([f"headline over {HEADLINE_MAX} chars"] if over else []) +
                (["headline not one line"] if multiline else []))
            demoted.append({"headline": f.get("headline", "(no headline)"),
                            "source_url": f.get("source_url", ""),
                            "reason": reason})
        else:
            passed.append(f)
    passed.sort(key=lambda f: (SEV_ORDER[f["severity"]],
                               OWNER_ORDER[f["owner"]]))
    return passed, demoted


def source_label(url):
    host = re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0]
    for dom, label in PRIMARY_LABELS.items():
        if host == dom or host.endswith("." + dom):
            return label
    return host or "source"


def direction(delta):
    d = delta.strip().lower()
    if d.startswith(("+", "up")) or d[:24].count("rose"):
        return "▲"
    if d.startswith(("-", "down", "below")) or d[:24].count("fell"):
        return "▼"
    return ""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip())
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = sys.argv[2] if len(sys.argv) > 2 else \
        f"LKG-Sector-Digest-{data['date']}.docx"

    flags, demoted = gate(data.get("flags", []))
    watchlist = demoted + list(data.get("watchlist", []))

    try:
        from docx import Document
        from docx.shared import Pt, Cm, RGBColor
        from docx.opc.constants import RELATIONSHIP_TYPE as RT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
    except ImportError:
        sys.exit("python-docx not installed (pip install python-docx). "
                 "Gate result: %d flag(s) passed, %d demoted." %
                 (len(flags), len(demoted)))

    BLUE = RGBColor(0x1F, 0x4E, 0x79)
    RED = RGBColor(0xC0, 0x00, 0x00)
    GREEN = RGBColor(0x2E, 0x7D, 0x32)
    AMBER = RGBColor(0xBF, 0x8F, 0x00)
    GREY = RGBColor(0x59, 0x59, 0x59)
    SEV_COLOR = {"high": RED, "med": AMBER, "low": GREY}

    def hyperlink(par, text, url, size=9):
        r_id = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
        hl = OxmlElement("w:hyperlink")
        hl.set(qn("r:id"), r_id)
        run, rpr = OxmlElement("w:r"), OxmlElement("w:rPr")
        for tag, attr in (("w:color", "1F4E79"), ("w:u", "single"),
                          ("w:sz", str(size * 2))):
            el = OxmlElement(tag)
            el.set(qn("w:val"), attr)
            rpr.append(el)
        rpr.append(OxmlElement("w:i"))
        run.append(rpr)
        t = OxmlElement("w:t")
        t.text = text
        run.append(t)
        hl.append(run)
        par._p.append(hl)

    def bold_numbers(par, text, size=10, color=None):
        for piece in NUM_RE.split(text):
            if not piece:
                continue
            r = par.add_run(piece)
            r.bold = bool(NUM_RE.fullmatch(piece))
            r.font.size = Pt(size)
            if color:
                r.font.color.rgb = color
        return par

    def label_cell(cell, text):
        r = cell.paragraphs[0].add_run(text)
        r.bold, r.font.size, r.font.color.rgb = True, Pt(9), GREY

    def source_block(par, url):
        # hyperlinked short label for the screen, full URL in small grey for
        # print — a citation must survive on paper
        hyperlink(par, source_label(url), url)
        br = par.add_run()
        br.add_break()
        r = par.add_run(url)
        r.font.size, r.font.color.rgb = Pt(7.5), GREY

    def set_widths(table, cms):
        # fixed layout so every table of a kind shares identical column lines
        table.autofit = False
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        table._tbl.tblPr.append(layout)
        for row in table.rows:
            for cell, w in zip(row.cells, cms):
                cell.width = Cm(w)

    def section(title):
        h = doc.add_heading(title, 1)
        h.paragraph_format.page_break_before = True
        return h

    doc = Document()
    for s in ("Title", "Heading 1", "Heading 2", "Heading 3"):
        doc.styles[s].font.color.rgb = BLUE
    doc.styles["Heading 1"].paragraph_format.space_before = Pt(14)

    doc.add_heading(f"LKG Portfolio Sector Digest — {data['date']}", 0)
    hdr = doc.add_paragraph()
    hdr.add_run(
        f"Run: {data.get('run_time', '')} · Sources scanned: "
        f"{data.get('sources_scanned', '?')} · ").italic = True
    d = hdr.add_run(f"DRAFT — for review by {data.get('reviewer', '[name]')}")
    d.bold, d.font.color.rgb = True, RED

    # At a glance — deterministic summary assembled from the gated data only
    doc.add_heading("At a glance", 1)
    owners = [f["owner"] for f in flags]
    sevs = [f["severity"] for f in flags]
    summ = doc.add_paragraph()
    if flags:
        groups = ", ".join(p for p in (
            f"{owners.count('board')} for the Board" if "board" in owners else "",
            f"{owners.count('QLC')} for QLC" if "QLC" in owners else "",
            f"{owners.count('GM')} for the GM" if "GM" in owners else "") if p)
        bold_numbers(summ,
                     f"This digest nominates {len(flags)} item(s) for review — "
                     f"{groups} ({sevs.count('high')} high / "
                     f"{sevs.count('med')} med / {sevs.count('low')} low). "
                     f"Top item: {flags[0]['headline']}. ")
    else:
        summ.add_run("No items passed the flag gate this run. "
                     ).font.size = Pt(10)
    bold_numbers(summ,
                 f"The Watchlist holds {len(watchlist)} item(s)" +
                 (f", {len(demoted)} demoted by the flag gate with the "
                  f"failure named" if demoted else "") +
                 ". Every flag is a nomination — nothing is distributed until "
                 "the reviewer completes section 6.")

    single_sector = len({f.get("sector") for f in flags}) <= 1
    sector_name = data["sectors"][0]["name"] if data.get("sectors") else ""
    section("1. Flagged items" +
            (f" — {sector_name}" if single_sector and sector_name
             and flags else ""))
    leg = doc.add_paragraph()
    r = leg.add_run("Severity: HIGH = act this week · MED = discuss at the "
                    "next GM/board touchpoint · LOW = context. "
                    "Grouped by who reviews.")
    r.italic, r.font.size, r.font.color.rgb = True, Pt(9), GREY
    if not flags:
        doc.add_paragraph("No items passed the flag gate this run.")
    for owner, gtitle in (("board", "For the Board"),
                          ("QLC", "For QLC — deal flow"),
                          ("GM", "For the GM")):
        group = [f for f in flags if f["owner"] == owner]
        if not group:
            continue
        doc.add_heading(gtitle, 2)
        for f in group:
            head = doc.add_heading("", 3)
            tag = head.add_run(f"[{f['severity'].upper()}]  ")
            tag.font.color.rgb = SEV_COLOR[f["severity"]]
            head.add_run(f["headline"])
            t = doc.add_table(rows=0, cols=2)
            t.style = "Light Grid Accent 1"
            rows = [("Why this matters", f.get("implication", "")),
                    ("Mechanism", f"{f.get('mechanism', '')} · "
                                  f"{f.get('polarity', '')}")]
            if not single_sector:
                rows.append(("Sector", f.get("sector", "")))
            for k, v in rows:
                cells = t.add_row().cells
                label_cell(cells[0], k)
                bold_numbers(cells[1].paragraphs[0], v)
            cells = t.add_row().cells
            label_cell(cells[0], "Source")
            source_block(cells[1].paragraphs[0], f["source_url"])
            set_widths(t, (3.5, 12.5))

    section("2. Macro dashboard")
    if data.get("macro"):
        touched = {s for m in data["macro"]
                   for s in m.get("sectors_touched", [])}
        multi = len(touched) > 1
        cols = ("Indicator", "Delta") + \
            (("Sectors touched",) if multi else ()) + ("Source",)
        t = doc.add_table(rows=1, cols=len(cols))
        t.style = "Light Grid Accent 1"
        for i, h in enumerate(cols):
            t.rows[0].cells[i].paragraphs[0].add_run(h).bold = True
        for m in data["macro"]:
            cells = t.add_row().cells
            cells[0].paragraphs[0].add_run(
                m.get("indicator", "")).font.size = Pt(10)
            p = cells[1].paragraphs[0]
            glyph = direction(m.get("delta", ""))
            if glyph:
                g = p.add_run(glyph + " ")
                g.bold = True
                g.font.color.rgb = RED if glyph == "▼" else GREEN
            bold_numbers(p, m.get("delta", ""))
            i = 2
            if multi:
                cells[2].paragraphs[0].add_run(", ".join(
                    m.get("sectors_touched", []))).font.size = Pt(10)
                i = 3
            if m.get("source_url"):
                source_block(cells[i].paragraphs[0], m["source_url"])
        set_widths(t, (4.5, 6.0, 2.5, 3.0) if multi else (5.0, 7.0, 4.0))
    else:
        doc.add_paragraph("No macro deltas this run (deltas only — "
                          "non-events are not reported).")

    section("3. Sector sections")
    for s in data.get("sectors", []):
        doc.add_heading(f"{s['name']} ({s.get('status', 'active')})", 2)
        if s.get("status") == "stub":
            doc.add_paragraph(s.get(
                "note", "not yet configured — sectors onboarded deliberately"))
            continue
        for it in s.get("items", []):
            p = doc.add_paragraph(style="List Bullet")
            aud = it.get("audience", "?")
            r = p.add_run(f"[{'Board' if aud == 'board' else aud}]  ")
            r.bold, r.font.size = True, Pt(10)
            bold_numbers(p, f"{it['headline']}. ")
            lbl = p.add_run("Why this matters: ")
            lbl.italic, lbl.font.size, lbl.font.color.rgb = True, Pt(10), GREY
            bold_numbers(p, f"{it.get('implication', '')} ")
            if it.get("source_url"):
                hyperlink(p, f"({source_label(it['source_url'])})",
                          it["source_url"])
                p.add_run().add_break()
                r = p.add_run(it["source_url"])
                r.font.size, r.font.color.rgb = Pt(7.5), GREY

    section("4. Watchlist")
    for w in watchlist:
        p = doc.add_paragraph(style="List Bullet")
        bold_numbers(p, w["headline"] + " ")
        r = p.add_run(f"— {w.get('reason', '')} ")
        r.italic, r.font.size, r.font.color.rgb = True, Pt(10), GREY
        if w.get("source_url"):
            hyperlink(p, f"({source_label(w['source_url'])})", w["source_url"])
            p.add_run().add_break()
            r = p.add_run(w["source_url"])
            r.font.size, r.font.color.rgb = Pt(7.5), GREY
    if not watchlist:
        doc.add_paragraph("Empty.")

    section("5. Assumptions appendix")
    for a in data.get("assumptions", []):
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(a)
        r.font.size, r.font.color.rgb = Pt(9), GREY
        p.paragraph_format.space_after = Pt(2)

    section("6. Reviewer decisions")
    t = doc.add_table(rows=1, cols=3)
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(("Flag", "Decision", "Reviewer comment")):
        t.rows[0].cells[i].paragraphs[0].add_run(h).bold = True
    for f in flags:
        cells = t.add_row().cells
        p0 = cells[0].paragraphs[0]
        tag = p0.add_run(f"[{f['severity'].upper()}] ")
        tag.bold, tag.font.size = True, Pt(10)
        tag.font.color.rgb = SEV_COLOR[f["severity"]]
        p0.add_run(f["headline"]).font.size = Pt(10)
        p1 = cells[1].paragraphs[0]
        for j, opt in enumerate(("☐ Promote", "☐ Reject", "☐ Amend")):
            r = p1.add_run(opt)
            r.font.size = Pt(9)
            if j < 2:
                r.add_break()
    if not flags:
        t.add_row().cells[0].paragraphs[0].add_run(
            "(no flags passed the gate this run)").font.size = Pt(10)
    set_widths(t, (8.8, 3.2, 4.0))
    sig = doc.add_paragraph()
    sig.add_run("Reviewed by: ____________________    Date: ____________"
                ).bold = True
    doc.add_paragraph("No item in section 1 is distributed until its row "
                      "above is completed.")

    for p in doc.paragraphs:
        if p.style.name.startswith(("Heading", "Title")):
            continue
        for r in p.runs:
            if r.font.size is None:
                r.font.size = Pt(10)
    doc.save(out)
    print(f"wrote {out}: {len(flags)} flag(s), {len(demoted)} demoted to "
          f"watchlist by gate, {len(data.get('sectors', []))} sector(s)")


if __name__ == "__main__":
    main()
