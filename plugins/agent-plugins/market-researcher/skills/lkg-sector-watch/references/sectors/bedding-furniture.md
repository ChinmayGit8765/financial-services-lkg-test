# Sector: Australian bedding & furniture retail

**Weighting:** risk-weighted · **Depth:** PRIMARY — full scan every run.
**Provenance:** player map and linkages compiled from public sources (news, ASX
filings); nothing here draws on internal Hypnos/QLC data.
LKG exposure: Hypnos Group (QLC portfolio) — Snooze + FutureSleep + G&G Furniture,
Australia's largest vertically-integrated bedding/furniture retailer. **Snooze is a
franchise network** — franchise-system news anywhere in Australian retail is
in-scope for this sector.

## Player map

| Player | Relationship | Filings spine |
|---|---|---|
| Snooze / FutureSleep / G&G Furniture | **ours** (Hypnos, QLC portfolio) | private — news only |
| Forty Winks | competitor | private — news only |
| Nick Scali | competitor | ASX: NCK |
| Adairs | competitor | ASX: ADH |
| Harvey Norman / Domayne | competitor | ASX: HVN |
| Temple & Webster | competitor (online) | ASX: TPW |
| Koala, Sleeping Duck, Ecosa | competitors (DTC) | private — news only |
| IKEA | competitor | private — news only |
| AH Beard, Sealy, Sleepmaker | suppliers | news only |

ASX-listed names are the filings spine — scan their announcement pages first.

## Source menu (draw the scan from here)

1. ASX announcements: NCK, ADH, HVN, TPW (one query covers all four)
2. AFR / general business news search on the player names above
3. ACCC media releases + franchising news (Snooze network risk)
4. ABS housing / CoreLogic turnover release (macro)
5. RBA decisions + Westpac–MI consumer sentiment (macro)
6. Demand-signals lane (run via the `demand-scout` subagent): new-homeowner and
   moving activity, first-home-buyer lending, renovation approvals — the
   upstream events that put a mattress or a bedroom suite on a shopping list

**Prefer primary sources** — ACCC, Cotality, ABS, Westpac IQ, ASX announcements —
over aggregators, law-firm summaries, and property-commentary sites; a figure
available from its originator is cited from its originator.

## Encoded linkages (mechanism IDs — frozen)

Context the agent applies; never forecasts it makes. Report signal + mechanism +
handoff.

| ID | Linkage |
|---|---|
| `housing-turnover` | Housing turnover → bedding demand: moves drive mattress purchases |
| `rates-sentiment` | RBA rate decisions / consumer sentiment → discretionary spend |
| `input-costs` | Freight + foam/timber input costs → margin pressure sector-wide |
| `seasonality` | Calendar: Boxing Day, EOFY, Black Friday, spring housing peak |
| `franchise-risk` | Franchising Code changes, ACCC actions, franchisee disputes anywhere in retail → Snooze network risk |
| `ma-distress` | Administrations, store-network shrinkage, divestments, PE exits → QLC deal-flow (owner: QLC) |
| `competitor-move` | Competitor promotions, pricing, store openings/closures, share shifts |

## Flag emphasis (what gets promoted, in order)

1. **M&A / distress signals** — administrations, store-network shrinkage,
   divestments, PE exits. This is QLC deal-flow language; owner is QLC.
2. **Franchise-network risk** — Franchising Code, ACCC enforcement, franchisee
   disputes in any retail system, not just bedding.
3. **Competitor promotions / share shifts** — especially around seasonality windows.
4. **Macro threshold-crossings** — deltas only, never "RBA held".

## International context (static — NOT a daily scan target)

Tempur Sealy's scale consolidation, Sleep Number's discretionary-spend sensitivity,
and the DTC mattress shakeout (bed-in-a-box consolidation) are background for
interpreting local moves. Cite only when a local item echoes one of these patterns.
