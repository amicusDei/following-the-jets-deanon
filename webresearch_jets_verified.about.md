# webresearch_jets_verified.csv — home-base verification of web-researched jets

**What:** The 78 web-researched FAA jets verified against each firm's HQ airport via OpenSky. One row = one jet.

**Columns:** `ticker` · `tail` · `icao24` · `owner` (FAA) · `n_flights` · `home_base` (modal airport) · `km_to_hq` · `verdict` (`CONFIRMED` if ≤100 km, else `rejected_far`/`insufficient`).

**Source:** OpenSky Trino `flights_data4` + airport coords. **Finding:** 59 CONFIRMED across 29 firms (Ford→Detroit, JPMorgan→White Plains 0 km, Chevron→Sugar Land 0 km, GM, Goldman, Morgan Stanley, MGM, Wynn, 3M…); 19 rejected. Resolved the `N113CS` conflict (Schwab rejected → Blackstone's).

**Use:** CONFIRMED rows were added to `dealmaker_jets.csv` (source=`webresearch`), expanding it to 111 firms.
