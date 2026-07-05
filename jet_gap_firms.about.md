# jet_gap_firms.csv — firms that disclosed a jet in SEC but we had none (77 firms)

**What:** S&P 500 firms whose SEC filings disclose a corporate jet but which had **no** identified jet in our set — the targets of the web-research jet pass. One row = one firm.

**Columns:** `ticker` · `sp_name` · `perq_def14a` · `timeshare` · `ex21_avi` (SEC aircraft-signal counts; `-1` = transient query error).

**Source:** `sec_aircraft_signals_302.csv` (disclosed a jet) minus firms already in `dealmaker_jets.csv`. **Examples:** Bristol-Myers, Chevron, Comcast, Pfizer, AbbVie, Salesforce, JPMorgan, Goldman, Ford, GM, Alphabet, 3M.

**Use:** the input to the 7-agent web-research jet pass (→ `webresearch_jets_faa.csv`).
