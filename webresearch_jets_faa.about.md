# webresearch_jets_faa.csv — web-researched tails resolved to FAA business jets (78 jets)

**What:** Tail numbers found by deep web research (SEC time-sharing exhibits + aviation databases) for the 77 gap firms, resolved to **active FAA business jets**. One row = one jet (pre-home-base-verification).

**Columns:** `ticker` · `tail` · `icao24` (FAA hex) · `owner` (FAA registered owner) · `mfr`/`model` · `state`.

**Source:** 7 web-research agents → 111 candidate tails → FAA active-business-jet match (drops historical/sold/turboprop). **Note:** mix of direct corporate owners (GM/Global Services Detroit, JPMorgan Chase Bank, PNC) and trustees (TVPX, Bank of Utah, US Bank, CSC Delaware).

**Use:** input to the home-base verification (`webresearch_jets_verified.csv`).
