# Run guide — LKG Portfolio Sector Digest

How to install, trigger, and verify a digest run. What the adaptation *is* lives
in [LKG-ADAPTATION.md](LKG-ADAPTATION.md); where it runs beyond the demo lives in
[DEPLOYMENT.md](DEPLOYMENT.md). This is the operator's page.

## Prerequisites

- **Claude Code** (or Cowork) with web search available — the scan is public-web only.
- **Python 3.9+** with `python-docx` (`pip install python-docx`) for the .docx
  render. Without it the renderer still runs the flag gate and prints the verdict
  (`N flag(s) passed, N demoted`) — only the document itself needs the library.
- **No connectors, no API keys.** CapIQ/FactSet are declared in the tool
  allowlist but absent by design; public sources substitute, disclosed per run.

## Install

From GitHub (both `main` and `lkg-adaptation` carry the adaptation):

```bash
claude plugin marketplace add ChinmayGit8765/financial-services-lkg-test
claude plugin install market-researcher@lkg-financial-services
```

From a local clone (development):

```bash
claude plugin marketplace add ./financial-services-lkg-test
claude plugin install market-researcher@lkg-financial-services
```

The marketplace is named `lkg-financial-services`, not the upstream name — the
upstream name is reserved to `github.com/anthropics` and Claude Code rejects it
on install (error cited verbatim in [LKG-ADAPTATION.md](LKG-ADAPTATION.md)).

Cowork: **Settings → Plugins → Add plugin**, paste the repo URL, pick
**Market Researcher** — or zip `plugins/agent-plugins/market-researcher/` and
upload that.

## Run a digest

In a session with the plugin installed, say any trigger phrase:

> "LKG sector digest" · "sector digest" · "portfolio watch" · "daily digest" ·
> "what moved in bedding"

The `market-researcher` agent enters digest mode and `lkg-sector-watch` drives.
A full run is **~25–30 min scan-to-draft** (recorded 22 Jul run). You will see,
in order:

1. **Sector registry load** — Australian bedding & furniture retail (PRIMARY,
   full scan); NBL and Brand Collective are named next candidates, deliberately
   not yet onboarded.
2. **Source sweep** — capped at 5–8 sources, all on the primary sector; ASX
   announcements of the listed names first, then sector news, then macro.
3. **Candidate extraction** — each item needs a source URL and, to matter, a
   mechanism ID from the sector file. Macro items only on a delta.
4. **Audience classification** — one batched `audience-classifier` subagent
   call returns `GM | board | noise` + rationale per item, JSON only.
5. **Flag gate** — seven required fields or the item drops to the Watchlist
   with the missing field named.
6. **Render** — digest JSON → `LKG-Sector-Digest-<YYYY-MM-DD>.docx` via
   `scripts/build_digest.py`, which re-runs the gate at render time.
7. **Stop.** The agent presents the file path and flag count and waits. The
   header reads `DRAFT — for review by [name]`; promotion is yours, and the
   agent never emails, schedules, or distributes.

## Render or replay manually

```bash
python plugins/agent-plugins/market-researcher/skills/lkg-sector-watch/scripts/build_digest.py digest.json "LKG-Sector-Digest-2026-07-22.docx"
```

(`py -3` on Windows if `python`/`python3` doesn't resolve. JSON schema is in the
skill's `references/digest-template.md`.)

Re-running the renderer on a saved digest JSON is the audit replay: same input,
same flags, same demotions, deterministically. Editing a field in the JSON and
re-rendering shows exactly what the gate does with it.

## Verify a run

- Header carries `DRAFT — for review by [name]`, date, run window, and sweep count.
- Every flag has all seven fields; headline is one line, ≤140 chars; mechanism
  is from the frozen taxonomy in `references/sectors/`.
- Anything demoted appears in the Watchlist **with its failure reason named**.
- Assumptions appendix is present: sources swept, broker-research substitute,
  connector blind spots, recency window, any synthetic elements.
- Snooze/Hypnos items cite public sources only (related-party rule).

## Changing the skill

Edit under `plugins/vertical-plugins/equity-research/skills/lkg-sector-watch/`,
then propagate and lint:

```bash
python scripts/sync-agent-skills.py   # copy into the agent bundle
python scripts/check.py               # manifests, path refs, copy drift; installs the version-bump hook
```

Adding a sector = one file under `references/sectors/` + one registry row in
`SKILL.md` + its mechanism IDs added to `MECHANISMS` in `build_digest.py` —
the gate rejects mechanism IDs it doesn't know, so a sector isn't live until
all three land together.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Failed to add marketplace: … name … reserved for official Anthropic marketplaces` | Fork still carries the upstream marketplace name — this repo already ships renamed; pull latest. |
| `python3` not found (Windows) | Use `py -3` or `python`. |
| Renderer exits with `python-docx not installed` | `pip install python-docx`. The printed gate result is still valid. |
| Digest trigger phrase doesn't fire the skill | Confirm `market-researcher@lkg-financial-services` is installed; or ask explicitly to "run the lkg-sector-watch skill". |
| A flag you expected shows up in the Watchlist | Read the demotion reason in that row — missing field, bad enum, or headline over 140 chars / multi-line. Fix the JSON, re-render. |
| Commit didn't bump a plugin version | `version_bump.py` bumps once per branch, not per commit — the branch ends one patch ahead of `main`. See `scripts/check.py`. |
