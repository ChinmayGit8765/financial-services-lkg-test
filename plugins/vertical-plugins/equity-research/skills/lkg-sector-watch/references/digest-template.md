# Digest document structure & JSON schema

The output document IS a **Daily Digest**: `LKG Portfolio Sector Digest — {date}`,
delivered as `.docx`. Structure is fixed; `scripts/build_digest.py` renders it from
the JSON below and re-enforces the flag gate at render time.

## Document structure

**Header block** — date · run time · sources scanned count ·
`DRAFT — for review by [name]` (rendered red), followed by an **At a glance**
paragraph — flag count by audience and severity, top item, Watchlist count —
assembled deterministically from the gated JSON, never model prose.

1. **Flagged items** — grouped **For the Board / For QLC / For the GM**,
   severity-sorted within each group with colour-coded severity tags. Key
   numbers render bold; every source renders as a hyperlinked label (originator
   name for primaries — Cotality, ABS, ACCC — bare domain for secondaries)
   with the full URL beneath it in small grey print, so citations survive on
   paper and projector alike.
2. **Macro dashboard** — rates, housing, sentiment. Each row: indicator, delta,
   sectors touched. Deltas/threshold-crossings only.
3. **Sector sections** — one per registry sector (today: bedding & furniture,
   deep). Per item: headline, source, GM/board tag, one-line implication.
4. **Watchlist** — items that failed the flag gate (with the missing field named)
   or aren't yet material.
5. **Assumptions appendix** — sources used and why; what substitutes for broker
   research (public news + ASX announcements); any synthetic elements; known
   blind spots without licensed connectors (CapIQ/FactSet); source-recency window.
6. **Reviewer decisions** — one row per gated flag: shortened flag reference ·
   ☐ Promote / ☐ Reject / ☐ Amend checkboxes · Reviewer comment (left blank),
   then a signature block. The renderer emits this section unfilled by design —
   only the named human completes it, and no item in section 1 is distributed
   until its row is.

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
