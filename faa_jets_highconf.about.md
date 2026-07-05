# faa_jets_highconf.csv — high-confidence FAA name-match jets (15 firms / 43 jets)

**What:** The reliable cut of `faa_jets_identified.csv`: jets whose FAA owner name matches the firm **and** whose owner is registered in the firm's HQ state. One row = one verified jet.

**Columns:** `ticker` · `firm` · `N` (tail) · `hex` (icao24) · `NAME` (FAA owner) · `CITY`/`STATE` · `hq_state` · `state_match` (True) · `MFR`/`MODEL`.

**Source:** FAA Releasable Aircraft Database, name-AND-match confirmed by HQ-state. **Examples:** Chevron G650ERs (Sugar Land TX), Union Pacific Falcons (Omaha), Kimberly-Clark Gulfstreams (Dallas), ONEOK Challengers (Tulsa).

**Use:** the firms the FAA registry alone can identify (distinctive names registered openly); the rest need SEC/OpenSky deanon.
