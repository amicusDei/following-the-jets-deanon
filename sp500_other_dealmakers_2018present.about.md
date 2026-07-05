# sp500_other_dealmakers_2018present.csv — S&P 500 M&A dealmakers outside the cohort (405 firms)

**What:** S&P 500 firms (point-in-time members 2018–present) that made ≥1 M&A deal >$500M and are **not** in the 133-firm nwejets cohort. One row = one firm.

**Columns:** `cusip6` (issuer CUSIP) · `sp_name` (CRSP index name) · `ticker` · `n_deals` (>$500M deals) · `total_musd` (Σ deal value, $M) · `first_deal`/`last_deal` (date range).

**Source:** WRDS/SDC `tr_sdc_ma.wrds_ma_details` (deal_value>500), S&P 500 membership from CRSP `dsp500list`, acquirer matched by `acusip`. **Caveat:** includes self-deals/buybacks; `total_musd` carries SDC outliers — `n_deals` is the more robust ranking field.

**Use:** the universe of "other" dealmakers we don't yet track — the jet-identification target pool.
