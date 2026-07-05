# sp500_dealmaker_jet_coverage.csv — jet coverage of the S&P 500 dealmakers (384 firms)

**What:** Cross-reference of S&P 500 true-acquisition dealmakers (>$500M) against the business-jet data we hold. One row = one firm.

**Columns:** `ticker` · `sp_name` · `n_deals` · `total_musd` · `in_cohort` (in the 133-firm set) · `n_biz_jets` (business jets in our data) · `jetless` (1 = no business jet).

**Source:** WRDS/SDC dealmakers ⨯ `jets.csv`/widened-DB jet counts. **Headline:** 76 of 384 had jets at the start; `jetless==1` firms are the recovery targets driven through the SEC→FAA→OpenSky pipeline.

**Use:** the gap analysis that scoped the whole jet-recovery effort.
