# jet_identification_targets.csv — jetless dealmakers + HQ for FAA matching (299 firms)

**What:** The jetless S&P 500 dealmakers (>$500M) with their corporate HQ address — the input list for FAA registry / OpenSky jet identification. One row = one firm.

**Columns:** `ticker` · `sp_name` · `conm` (Compustat name) · `n_deals` · `total_musd` · `add1`/`city`/`state`/`addzip` (HQ address) · `weburl` · `cusip6`.

**Source:** jetless dealmakers (`sp500_dealmaker_jet_coverage`) enriched with Compustat HQ (`comp.company` via `comp.security`). **Caveat:** ~18 rows where the CUSIP matched a bond/unit security lack a clean HQ.

**Use:** HQ address is needed because corporate jets register to LLCs/trustees, so name matching fails — address/metro is the FAA-matching anchor.
