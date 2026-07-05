# 82-firm rerun + overlooked-deal exploration

Two asks: (1) rerun the widened backtest with the 82-firm jet set, (2) find deals we overlooked.
Both land on the same wall — and it's not jet visibility.

## 1. Baseline widened backtest (reproduced)

`deanon/analyze_widened.py` on `backtest_wide.db` reproduces `WIDENED-RESULTS.md` exactly:

| set | deals | firms | within-pair |
|---|---|---|---|
| original_133 | 208 | 73 | 1.49× (p=1.4e-3) |
| widened_all | 554 | 202 | **1.38× (p=5.0e-5)** |
| coverage-gated | 440 | 170 | 1.24× (p=2.2e-3) |
| **placebo (null-matched)** | 614 | 214 | **1.11× (p_clustered=0.19 — NULL)** |

The within-pair enrichment is real arithmetically but the **placebo is null** — the proper
calendar/activity-matched comparison shows no effect. This is the Reviewer-2 verdict: the ~1.4×
is a control-design artifact, not alpha.

## 2. The 82-firm rerun: the 6 new firms add ~nothing

The 6 SEC+home-base–recovered firms (AIG, BAC, BDX, BX, CAH, V) are **not in `backtest_wide.db`** —
no firm record, no geocoded deal targets. To enter the panel, their deals' **target HQs must be
geocoded**. Result:

- 6 new firms made **65 M&A deals >$100M** (2018–present).
- **Only 5 have a public, geocodable target HQ** — and several of those are foreign (Toronto,
  Beijing) or mis-geocoded. Net usable: **~2–3 deals.**

So the entire recovery chain (SEC time-share → FAA → OpenSky home-base → deanon, 76→82 firms,
+8 jets) contributes **a handful of testable deals** — far too few to move the 554-deal / 1.38×
result, and the placebo stays null. A full `backtest_wide.db` rebuild for ~3 deals is not worth it
and would not change the conclusion.

## 3. Overlooked deals — and why most can't be recovered

Full M&A universe of the 82 jet-firms, 2018–present (WRDS/SDC, excl self-deals) →
`jetfirm_all_deals_82.csv`:

- **1,063 deals total** (218 >$500M, 331 >$100M) — far more than the backtest's ~554 within-pair.
- **Target-type breakdown — the binding constraint:**

| target | deals | share | geocodable? |
|---|---|---|---|
| Private | 575 | 54% | no (no public HQ) |
| Subsidiary | 359 | 34% | rarely |
| **Public** | **111** | **10%** | **yes (Compustat)** |
| JV / Govt | 18 | 2% | n/a |

**88% of these firms' deals have a private or subsidiary target** whose HQ isn't in any registry —
so the jet has no geocodable place to "visit," regardless of how well we track the jet. Only ~10%
(public targets) are testable. The overlooked deals are overwhelmingly **un-recoverable for a
target-side reason, not a jet-side one.**

## Bottom line

Both asks resolve to the same conclusion the project already reached: **the binding constraint is
target privacy + break scarcity, not acquirer-jet visibility.** We materially improved jet coverage
this session (76→82 firms, free-data SEC/FAA/OpenSky pipeline), but it buys almost no new testable
deals because the targets these firms buy are overwhelmingly private. Rerunning confirms a **stable
~1.4× within-pair that is null under placebo** — replication, not signal. Widening the acquirer
universe further will keep hitting the same 10%-public-target ceiling.

### Artifacts
- `jetfirm_all_deals_82.csv` — full 1,063-deal universe of the 82 jet-firms (target-type tagged)
- baseline numbers: `deanon/results/widened_results.json` (in the predfkitweball repo)
