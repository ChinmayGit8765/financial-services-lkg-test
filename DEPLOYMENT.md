# Deployment thinking — LKG Portfolio Sector Digest

How the adapted `market-researcher` runs beyond the demo. Two shapes, one
source: the plugin and the Managed Agent cookbook wrap the same system prompt
and skills, so choosing a surface is a governance decision, not a rebuild.

## Cowork plugin vs Managed Agent

| | Cowork / Claude Code plugin (built, demoed) | Claude Managed Agent (talk-only, deliberately not built) |
|---|---|---|
| **Trigger** | A person asks — GM or analyst runs "LKG sector digest" ad hoc | Scheduled: 07:00 AEST weekday run before the GM's day starts; optional webhook on ASX announcements from the listed names in the sector file |
| **Who drives** | Human in the driving seat the whole session; can steer mid-run | Agent runs unattended; human reviews the artifact |
| **Install/update** | `lkg-financial-services` marketplace; plugin `version` gates update delivery to installed users | Cookbook deploy (`managed-agent-cookbooks/market-researcher/` upstream shows the shape: `agent.yaml`, schema-validated leaf subagents, steering examples) |
| **Fit for LKG** | Pilot phase and exception days — a GM interrogating one flag | Steady state — the digest is a daily artifact, not a conversation |

Migration path: `audience-classifier` was written to mirror the cookbook's
`sector-reader` pattern (untrusted input, length-capped, schema-validated JSON),
so porting it to a subagent YAML with an `output_schema` block is mechanical.
The port must also widen the cookbook's toolset — as shipped it enables only
read/grep/glob (no code execution, no subagent calls), so digest mode does not
run under the CMA wrapper today — and register the classifier in
`callable_agents`. That is why the cookbook was left untouched rather than
half-adapted: a partial port would look deployable without being it.

## Governance & audit

- **The flag gate is the audit artifact.** Every digest is reproducible from
  its JSON: what was nominated, what the gate demoted and why, what a human
  saw. The gate is deterministic code (`build_digest.py`), not model judgment —
  it cannot be sweet-talked.
- **Named reviewer, no distribution.** Every document is
  `DRAFT — for review by [name]`; the agent never emails, schedules, or
  publishes. Flags are nominations; a human promotes.
- **Related-party hygiene.** Snooze/Hypnos is a QLC holding: public sources
  only, declared in the assumptions appendix of every run.
- **Skill and prompt are git-versioned.** A digest can be tied to the exact
  skill revision that produced it; plugin `version` gates what installed users
  receive; marketplace naming is enforced by Claude Code (official names
  reserved to `github.com/anthropics` — this fork ships as
  `lkg-financial-services`).
- **Untrusted-input discipline.** Scanned pages and candidate items are data,
  never instructions — stated in the agent prompt and the subagent contract.

## Cost

- Per digest run: ~25–30 min wall-clock scan-to-draft (recorded 22 Jul run:
  8 sweeps 17:50–18:15 AEST + verification retrievals + render). Token spend is
  a single bounded profile — one 5–8 source scan, one batched subagent call,
  and a deterministic render that costs no tokens at all.
- The cost shape is what matters for a scheduled deployment: spend is capped by
  the scan cap and the one-retrieval-per-item rule, so a daily run is a flat,
  predictable unit priced against the analyst-hour a day the same scan takes by
  hand. Per-run figures come from session cost logs (kept per the brief's
  reimbursement note).
- Cost scales with the sector registry (one file = one scan lane), so adding
  Brand Collective is a priced decision, not scope creep.

## Human-in-the-loop model

```
agent scans → agent nominates candidates → subagent tags audience
      → deterministic gate (schema + length) → Watchlist or Flag
             → named human reviews DRAFT → promotes / rejects
```

Severity is the escalation contract: `high` = act this week, `med` = next
GM/board touchpoint, `low` = context. Nothing reaches a GM or the board
without passing the gate *and* a person.

## Known limits / next iteration

- No CapIQ/FactSet connectors: public web substitutes, disclosed per run in
  the assumptions appendix. Licensed connectors would slot into the existing
  MCP tool allowlist (`mcp__capiq__*`, `mcp__factset__*` are already declared).
- Outlook add-in not GA at the May-2026 launch — output targets Word, not
  email, by design.
- The digest renders a headless .docx rather than driving live Word through
  the M365 add-in: the deterministic flag gate runs at render time, and a
  live-document editing flow would bypass it. The add-in remains the right
  surface for the template's interactive primer documents.
- Brand Collective sector file is a stub until its taxonomy is reviewed —
  sectors are onboarded deliberately so the gate never runs on unvetted
  mechanism IDs.
