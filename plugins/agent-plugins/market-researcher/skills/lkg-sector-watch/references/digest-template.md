# Digest document structure & JSON schema

The output document IS a **Daily Digest**: `LKG Portfolio Sector Digest — {date}`,
delivered as `.docx`. Structure is fixed; `scripts/build_digest.py` renders it from
the JSON below and re-enforces the flag gate at render time.

## Document structure

**Title block** — title (navy), sector · pretty date subtitle, then a red
`DRAFT — NOT FOR DISTRIBUTION` line carrying run time, sweep count, and the
named reviewer, closed by a navy rule. Section headings render as navy bands
(white uppercase) with a one-line grey italic subtitle each; colour is
semantic only (red = high/risk, amber = med, green = opportunity/up-delta,
grey = low/metadata).

1. **Flagged items** — severity legend, then one **flag card** per gated flag
   (severity-sorted, board/QLC before GM): a severity-tinted band with
   `SEV · AUDIENCE` badge and bold headline, a polarity · mechanism line, a
   literal **Why this matters:** line, and a hyperlinked source label
   (originator name for primaries — Cotality, ABS, ACCC — bare domain for
   secondaries) with a trailing ↗. No raw URLs in the body — every full URL
   lives in the Sources appendix.
2. **Macro dashboard** — navy header, zebra rows, ▲/▼ direction column
   (green/red). Deltas/threshold-crossings only.
3. **Sector detail** — the core section: per item a bold fact line tagged
   [Board]/[GM] plus an indented **Why this matters:** line and source link.
   Stub sectors render their one-line note only.
4. **Watchlist** — visually demoted (small, grey): uppercase status tag first
   (FAILED GATE / CLASSIFIED NOISE / NOT YET MATERIAL / …), then the item and
   source link. Items graduate to sections 1–3 when material.
5. **Assumptions & audit trail** — small grey bullets: sources used and why,
   broker-research substitute, synthetic elements, connector blind spots,
   recency window. Present but visually subordinate.
6. **Reviewer decisions** — red italic "no distribution until completed" line,
   then one row per gated flag: `[SEV · Audience]` + ~9-word flag reference ·
   ☐ Promote / ☐ Reject / ☐ Amend checkboxes · blank comment cell, and a
   sign-off line. The renderer emits this section unfilled by design — only
   the named human completes it.

**Appendix A — Sources** (new page) — every URL cited anywhere in the digest,
de-duplicated, in first-appearance order, tagged with the sections that cite
it. Body links resolve here; this is where citations survive on paper.

## Digest JSON schema (input to build_digest.py)

```json
{
  "date": "YYYY-MM-DD",
  "run_time": "HH:MM AEST",
  "reviewer": "Reviewer Name",
  "sources_scanned": 7,
  "flags": [
    {
      "headline": "one line, max 140 chars (gate demotes longer)",
      "source_url": "https://…",
      "polarity": "risk | opportunity | watch",
      "mechanism": "a mechanism ID from a sector file",
      "implication": "one line — why this matters, in plain language its reader takes in on first read",
      "owner": "GM | board | QLC",
      "severity": "low | med | high",
      "sector": "a sector id from the registry (today: bedding-furniture)"
    }
  ],
  "macro": [
    { "indicator": "RBA cash rate", "delta": "-25bp to 3.60%",
      "sectors_touched": ["bedding-furniture"], "source_url": "https://…" }
  ],
  "sectors": [
    {
      "name": "Australian bedding & furniture retail",
      "status": "active | light | stub",
      "note": "stub sections: the 'not yet configured' line",
      "items": [
        { "headline": "…", "source_url": "https://…",
          "audience": "GM | board", "implication": "one line" }
      ]
    }
  ],
  "watchlist": [
    { "headline": "…", "source_url": "https://…",
      "reason": "failed gate: missing mechanism | not yet material" }
  ],
  "assumptions": ["one bullet per assumption"]
}
```

Items the `audience-classifier` marks `noise` never reach `flags`; they land in
`watchlist` (with reason) or are dropped when they carry no mechanism at all.
