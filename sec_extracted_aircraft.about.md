# sec_extracted_aircraft.csv — tails/entities extracted from SEC documents (35 firms)

**What:** Tail numbers and aircraft entities regex-extracted from each firm's actual SEC time-sharing / Exhibit-21 documents. One row = one firm.

**Columns:** `ticker` · `sp_name` · `cik` · `tails` (`;`-joined N-numbers found) · `entities` (` | `-joined aviation LLC names) · `n_tails`.

**Source:** fetched EX-10.x / EX-21 documents from EDGAR (`www.sec.gov/Archives`), regex for `N#####` + `…Aviation/Aircraft LLC`. **Note:** required zero-padded CIK for EDGAR FTS; 12 firms yielded ≥1 tail (47 total).

**Use:** the raw tails before FAA resolution; e.g. Bristol-Myers → N404M/N410M/N552J/N554L.
