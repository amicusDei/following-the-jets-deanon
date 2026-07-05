# nwejets — jet de-anonymization & coverage expansion

The **jet-identification companion** to [`predfkitweball`](../predfkitweball) (the "can private-jet flights predict mergers?" investigation). This repo holds the pipeline that expands acquirer coverage — turning trustee/LLC-hidden corporate jets into named, home-base-verified aircraft using only free data — plus the analysis scripts and result figures from the widened re-run.

**Pipeline:** S&P-500 dealmakers (WRDS/SDC) → jet identification (FAA owner-name match → SEC filings → web research) → OpenSky home-base verification → deal-target-HQ geocoding.

## Final verdict

> **Expanding jet coverage does not rescue the signal — it independently confirms the null.**
>
> - The widened backtest (554 deals, 202 firms) shows a within-pair enrichment of **1.38× (p = 5×10⁻⁴)** that is arithmetically real but **collapses against a proper null-matched placebo (1.11×, p = 0.19)** — the same control-design artifact `predfkitweball` diagnosed.
> - The pre-deal flight "hump" (raw ~1.48×) **dissolves** under one-firm-one-vote, drop-outlier, and activity-matched controls. A 148-deal nearest-neighbour event model comes out at **chance**.
> - The binding constraint is **not** acquirer-jet visibility — it's **target privacy**: 88% of these firms' deals have private or subsidiary targets with no geocodable HQ, so only ~10% (public targets) are ever testable. Better jet tracking buys almost no new testable deals.
>
> A full free-data recovery pipeline (SEC time-share → FAA → OpenSky, 76 → 111 firms, +59 jets) is the engineering contribution; the scientific contribution is a clean, independent replication of the parent project's null.

See [`WIDENED-82FIRM-RESULTS.md`](WIDENED-82FIRM-RESULTS.md) (widened re-run + overlooked-deal analysis) and [`DEANON-302-RESEARCH.md`](DEANON-302-RESEARCH.md) (the LLC/trust de-anonymization playbook).

## Figures

`fig_eventstudy.png` · `fig_robustness.png` · `fig_critic.png` · `fig_post_hump.png` · `fig_calibration.png` — event study, robustness sweep, adversarial critic, post-announcement hump, and calibration.

## What's here

- **Scripts** (`*.py`) — jet identification (`sec_signal_pass.py`, `webresearch_jet_match.py`, `faa_*`), home-base verification (`confirm_homebase.py`, `webresearch_homebase_verify.py`, `opensky_confirm.py`), flight pulls (`pull_dealmaker_flights.py`), and the analysis/NN models (`nn_*.py`, `combine_model.py`, `critic_test.py`, `economic_context.py`, `make_*.py`).
- **Schema docs** (`*.about.md`) — a data dictionary for every dataset in the pipeline (columns, sources, key counts, caveats) — even though the datasets themselves are not shipped.

## Data note

**No datasets are included.** The underlying M&A data (SDC / Compustat, via WRDS) is **licensed** and cannot be redistributed; the flight, firm, and jet-identification tables are treated as private. Every dataset is reproducible from the scripts above given WRDS + OpenSky credentials; the `*.about.md` files document exactly what each one contains.
