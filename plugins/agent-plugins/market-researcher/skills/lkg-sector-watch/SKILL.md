---
name: lkg-sector-watch
description: Produce the LKG Portfolio Sector Digest — a daily scan of public sources across sectors LKG operates in (bedding/furniture retail via Hypnos Group, NBL, Brand Collective), with a deterministic flag gate that nominates items for GM, board, or QLC review. Triggers on "sector digest", "portfolio watch", "daily digest", "sector watch", "scan the sector", "LKG digest", or "what moved in bedding".
---

# LKG Sector Watch

Daily digest for the LKG portfolio. The agent scans public sources, applies each
sector's encoded linkages, and **nominates** flags. A named human reviewer promotes
them — nothing in this skill's output is a decision, a forecast, or a send.

## Sector registry

Sectors live one-per-file under `references/sectors/`. **Adding a sector = adding a
file** and one row here. The taxonomy inside each file is frozen — do not extend it
mid-run. Registry content is compiled from public sources only (news, ASX filings);
it encodes no internal LKG/QLC data.

| Sector file | Weighting | Depth |
|---|---|---|
| `references/sectors/bedding-furniture.md` | risk-weighted | PRIMARY — full scan |
| `references/sectors/nbl.md` | opportunity-weighted | SECONDARY — light, 3–4 sources |
| `references/sectors/brand-collective.md` | — | STUB — not yet configured |

## Workflow

### Step 1: Load sector context

Read every file in `references/sectors/`. Each defines the player map, the encoded
linkages (mechanism IDs), the flag emphasis, and its source menu. Linkages are
context the agent *applies* — never forecasts it makes.

### Step 2: Scan sources

- **Cap the scan at 5–8 sources total across all sectors** so runtime stays
  predictable. Take the PRIMARY sector's spine first (ASX announcements of listed
  names), then macro, then SECONDARY.
- Public data only: ASX filings, news, regulator releases, public broker
  commentary. No paywalled or employer data.
- Record the source menu swept and the run window in the assumptions appendix;
  the sweep count goes in the digest header. Every cited item carries its source
  URL. Verification retrievals (re-fetching a surfaced page to check a claim)
  are capped at one per candidate item and counted separately from the scan cap.

### Step 3: Extract candidate items

For each item found: headline, source URL, sector, one-line summary, and — if one
fired — the **mechanism ID** of the encoded linkage that makes it relevant. Macro
items are candidates **only on a delta or threshold-crossing** ("RBA cut 25bp"),
never on a non-event ("RBA held").

### Step 4: Classify audience

Hand the candidate items as JSON to the `audience-classifier` subagent. It returns
`GM | board | noise` with a one-line rationale per item. Items classified `noise`
skip the flag gate and go straight to the Watchlist (or are dropped if they carry
no mechanism at all).

### Step 5: Apply the flag gate (deterministic — no exceptions)

A flag exists only if **all** fields are present and valid; otherwise the item
drops to the Watchlist with the missing field named:

```yaml
flag:
  headline:      # one line, max 140 chars (renderer-enforced)
  source_url:    # required, real, must have been retrieved this run
  polarity:      # risk | opportunity | watch
  mechanism:     # a mechanism ID from the sector file that fired
  implication:   # one line, "why this matters"
  owner:         # GM | board | QLC
  severity:      # low | med | high
```

Owner rule: `owner` = the subagent's audience call, except items whose mechanism is
`ma-distress` (administrations, store-network shrinkage, divestments, PE exits) —
those are QLC deal-flow and get `owner: QLC`.

Severity guide: `high` = act-this-week for the owner; `med` = discuss at next
GM/board touchpoint; `low` = context worth having.

The gate is also enforced mechanically: `scripts/build_digest.py` re-validates
every flag and demotes any incomplete one to the Watchlist at render time.

### Step 6: Assemble the digest (.docx)

Write the digest JSON (schema in `references/digest-template.md`), then render:

```
python3 scripts/build_digest.py digest.json "LKG-Sector-Digest-<YYYY-MM-DD>.docx"
```

(`py -3` on Windows if `python3` doesn't resolve; the script lives in this
skill's `scripts/` directory — use its full path when running from elsewhere.)

The document is titled **"LKG Portfolio Sector Digest — {date}"** and follows the
structure in `references/digest-template.md`: Flagged items → Macro dashboard →
Sector sections → Watchlist → Assumptions appendix → Reviewer decisions. If
`python-docx` is not available in the session, produce the same structure via the
environment's Word / docx capability instead — structure is non-negotiable,
tooling is not.

### Step 7: Stop for human review

The header carries `DRAFT — for review by [name]`, and the document ends with the
Reviewer decisions table — one empty Promote / Reject / Amend row per flag that
only the named human completes. Present the file path and the flag count, then
stop. Every flag is a nomination; a human promotes it by completing its row.
Never email, distribute, or schedule anything.

## Important Notes

- **No probabilities or forecasts, anywhere.** Report the indicator, the linkage
  that fired, and the handoff — signal, mechanism, handoff. "Housing turnover up
  4.2% (ABS); moves drive mattress purchases; flagged for GM review" is correct.
  "Bedding demand likely to rise" is not.
- **Cite every item.** No source URL, no item — not even on the Watchlist.
- **Deltas only for macro.** A held rate, an unchanged index, a reiterated
  guidance range: not items.
- **Assumptions appendix is mandatory** — sources used and why, what substitutes
  for licensed broker research (public news + ASX announcements), any synthetic
  elements, known blind spots without CapIQ/FactSet connectors, and the
  source-recency window of this run.
- International context (Tempur Sealy, Sleep Number, DTC trends) is static
  background in the sector file — never a daily scan target.
