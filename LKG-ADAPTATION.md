# LKG Adaptation — requirements traceability

This fork adapts Anthropic's `market-researcher` template into the **LKG Portfolio
Sector Digest** for the LKG Group AI & Automation Specialist final interview.
Every brief constraint maps to a commit and file below; the walkthrough is
`git log 4aa51ed..HEAD` read top to bottom. To install and run it, see
[RUN-GUIDE.md](RUN-GUIDE.md).

## Brief constraint → where it's satisfied

| Brief requirement | Satisfied by |
|---|---|
| **Start from the Anthropic template, don't rebuild** | Fork of `anthropics/financial-services`; upstream history intact below `4aa51ed`. All changes are additive commits on top — the template's primer workflow still runs unmodified. |
| **At least one meaningful adaptation** | Three: new skill `lkg-sector-watch` (`c1367a7`), new subagent `audience-classifier` (`5b1b5d1`), tightened system prompt with LKG digest mode (`5915f85`). |
| **Public data only, no employer data** | Skill Step 2 + agent guardrail ("Public data only in digest mode"); related-party rule — Snooze/Hypnos is a QLC holding, public sources only, declared in every digest's assumptions appendix. |
| **Output lands in a real tool** | Word: `scripts/build_digest.py` renders the digest JSON to `.docx` deterministically (`c1367a7`, hardened `f89e3f1`). |
| **Human approval point explicit** | Flags are nominations. Skill Step 7 stops for review; every document header carries `DRAFT — for review by [name]`; agent guardrails forbid distribution. |
| **Document your assumptions** | Assumptions appendix is a mandatory digest section (sources, broker-research substitute, connector blind spots, recency window, synthetic elements). |
| **Daily digest cadence** | Document is titled and dated as a daily digest; scheduled-run deployment shape in [DEPLOYMENT.md](DEPLOYMENT.md). |

## "Sharp version" checklist (brief, p.2–3)

| Sharp-version item | Where |
|---|---|
| Skill that knows the players | `skills/lkg-sector-watch/references/sectors/bedding-furniture.md` — player map incl. Snooze/Forty Winks/Nick Scali/Adairs/Domayne, suppliers, ASX filings spine |
| 5–10 sources per run | Scan capped at 5–8 sources (skill Step 2) — keeps runtime predictable; the recorded 22 Jul end-to-end run took ~25 min scan-to-draft, so the live demo starts the run at the top of the slot and narrates the architecture over it, fallback .docx in hand |
| Subagent classifying GM vs board audience | `agents/audience-classifier.md` — GM / board / noise + one-line rationale, JSON-only |
| Sources cited, "why this matters" per item | Flag gate: `source_url` and `implication` are required fields — an item without either cannot be a flag |
| Deployable thinking | [DEPLOYMENT.md](DEPLOYMENT.md) |

## The governance gate (the core adaptation)

A flag exists only if all seven schema fields are present and valid
(`headline ≤140 chars, source_url, polarity, mechanism, implication, owner,
severity`). Enforced twice: in the skill instructions the agent reads, and
mechanically in `build_digest.py`, which re-validates at render time and demotes
failures to the Watchlist with the reason named. **Agents nominate, schemas
gate, humans promote.** The length rule (`f89e3f1`) was added after QA on the
first live run caught a 45-word headline the presence-check couldn't — the gate
is expected to grow this way: audit output, close the gap in code, not prose.

## Engineering found along the way

- `52d5416` — fixed a real Windows bug in the repo's own `version_bump.py`
  (backslashed paths broke `git show ref:path`; the pre-commit hook silently
  never bumped and `--check` false-passed locally while Linux CI would fail).
- `6705c0a` — marketplace renamed to `lkg-financial-services` after hitting
  Claude Code's supply-chain guardrail on install (observed verbatim):
  *"Failed to add marketplace: The name 'claude-for-financial-services' is
  reserved for official Anthropic marketplaces. Only repositories from
  'github.com/anthropics/' can use this name."*

## Deliberately not built

Managed Agent deployment (talk-only — see DEPLOYMENT.md), pptx/email output,
additional sectors beyond bedding/furniture — NBL and Brand Collective were
considered, prototyped, and cut before submission to maximise depth in the
primary sector; the registry pattern (one file = one sector) is the extension
path — and forecasts or probabilities anywhere in output.
