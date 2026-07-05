# sec_newly_identified_jets.csv — SEC-extracted tails resolved to FAA business jets (17 jets)

**What:** The SEC-extracted tails that resolve to an **active FAA business jet**. One row = one jet (pre-home-base-verification).

**Columns:** `ticker` · `sp_name` · `tail` · `icao24` (FAA hex) · `owner` (FAA registered owner) · `mfr`/`model` · `state` (registration state).

**Source:** `sec_extracted_aircraft.csv` tails ⨯ FAA active-business-jet registry. **Note:** 47 extracted tails → 17 active business jets across 9 firms; many behind trustees (Bank of Utah, UMB, US Bank, TVPX). Still includes false positives (e.g. BMY N410M = Zokaites) — filtered by `homebase_confirmed_17.csv`.

**Use:** SEC→FAA join output; the home-base step then confirms firm ownership.
