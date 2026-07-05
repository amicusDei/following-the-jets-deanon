# sp500_other_deals_detail_2018present.csv — deal-level detail, non-cohort dealmakers (851 deals)

**What:** Deal-level records for the 405 non-cohort S&P 500 dealmakers — **true acquisitions only** (self-deals/buybacks removed). One row = one deal.

**Columns:** `ticker` · `sp_name` · `acquirer`/`acquirer_parent` · `target` · `target_nation`/`tnationcode` · `target_public` (Public/Priv./Sub./JV) · `dateann`/`date_eff`/`date_withdrawn` · `status` · `deal_value_musd` · `rankval_musd` · `deal_no` · `acusip`.

**Source:** WRDS/SDC, deals >$500M, 2018-01-07 → present, acquirer ∈ S&P 500. **Coverage:** 699 Completed · 109 Pending · 37 Withdrawn.

**Use:** the deal records behind the dealmaker list; `target_public` flags which deals have a geocodable (public) target HQ.
