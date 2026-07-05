# jetfirm_all_deals_82.csv — full M&A deal universe of the jet-firms (1,063 deals)

**What:** Every M&A deal (any size, 2018–present, excl. self-deals) by the firms that have a confirmed jet — the deal universe the backtest can draw from. One row = one deal.

**Columns:** `acusip` (acquirer issuer CUSIP) · `acq` (acquirer) · `tgt` (target) · `deal_value` ($M) · `dateann` · `tpublic` (Public/Priv./Sub./J.V./Govt.) · `statuscode`.

**Source:** WRDS/SDC `tr_sdc_ma.wrds_ma_details`, acquirer ∈ the (then-82) jet-firms by `acusip`. **Key fact:** 1,063 deals but only 10% have Public (geocodable) targets — 54% Private, 34% Subsidiary; this is the target-privacy wall.

**Use:** the deal pool for geocoding; `target_hq_research.csv` supplies HQ coords for the researchable targets.
