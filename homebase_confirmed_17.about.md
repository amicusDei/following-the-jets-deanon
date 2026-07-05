# homebase_confirmed_17.csv — OpenSky home-base verification of the SEC-matched jets

**What:** The 17 SEC→FAA jets verified against each firm's HQ airport via OpenSky flight history. One row = one jet. The step that filters coincidental tail matches.

**Columns:** `ticker` · `tail` · `icao24` · `owner` (FAA) · `n_flights` · `home_base` (modal airport) · `km_to_hq` (distance home-base → firm HQ) · `verdict` (`CONFIRMED` if ≤80 km, else `rejected_far`/`insufficient`).

**Source:** OpenSky Trino `flights_data4` + airport coords. **Finding:** 8 CONFIRMED across 6 firms (AIG, BAC, BDX, BX, CAH, V); 9 rejected as false positives (e.g. BMY N410M → Butler PA; Bank-of-Utah tail → Dominican Republic).

**Use:** the decisive ownership filter; CONFIRMED rows entered the dealmaker jet set.
