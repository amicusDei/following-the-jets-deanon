# sec_aircraft_signals_302.csv — SEC aircraft-disclosure signal per jetless firm (270 firms)

**What:** EDGAR full-text-search signal for whether each jetless dealmaker discloses a corporate jet in SEC filings. One row = one firm.

**Columns:** `ticker` · `sp_name` · `total_musd` · `cik` · `perq_def14a` (# DEF 14A perquisite hits) · `timeshare` (# aircraft time-sharing/dry-lease exhibits — names the entity) · `ex21_avi` (# Exhibit-21 aviation subsidiaries) · `jet_disclosed` (bool) · `entity_namable` (bool). `-1` = transient query error (undercount).

**Source:** SEC EDGAR full-text search (`efts.sec.gov/LATEST/search-index`) per CIK. **Finding:** ~31% disclose a jet (lower bound); 35 firms name an aircraft entity → the addressable set. ~69% show no signal (fractional/charter/none).

**Use:** stratifies the jetless firms; `entity_namable` rows feed the SEC forward-match.
