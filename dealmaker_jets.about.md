# dealmaker_jets.csv — the consolidated dealmaker jet roster (204 jets / 111 firms)

**What:** The master roster of business jets attributed to S&P 500 >$500M dealmakers, accumulated across all identification methods. One row = one jet.

**Columns:** `icao24` (FAA hex) · `firm_id` (widened-DB id, or −2/−3 for session-added) · `tail` · `faa_model` · `ticker` · `name` (firm + provenance tag) · `source`.

**`source` provenance:** `widened` (136, from `backtest_wide.db`) · `webresearch` (59, SEC/aviation tails + home-base) · `sec_forward_match` (8, SEC time-share + home-base) · `deanon_session` (1, Broadcom N901MM).

**Source:** union of widened-DB jets + this session's SEC→FAA→OpenSky and web-research→FAA→OpenSky pipelines, every session-added jet home-base-confirmed.

**Use:** the canonical jet→firm key; flight activity for these icao24 is `dealmaker_flight_activity.csv`.
