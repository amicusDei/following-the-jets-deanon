# opensky_confirmed.csv — OpenSky home-base attribution of the candidate jets

**What:** The 4-firm candidate jets (`opensky_candidates_4firms.csv`) run through 8 years of OpenSky flight history to find each one's real home base and destination fingerprint. One row = one candidate jet.

**Columns:** `ticker` · `home` (firm home airport) · `N`/`hex`/`icao24` · `NAME` · `CITY`/`STATE` · `MFR`/`MODEL` · `n_flights` · `home_base` (modal airport) · `home_share` · `based_at_home` (bool) · `top_dest` (top destinations).

**Source:** OpenSky Trino `flights_data4` (2018–present), `pyopensky`. **Finding:** basing is confirmed for many, but NVDA≡AVGO share the KSJC pool (incl. unrelated VC/winery jets) — basing alone can't make the 1:1 firm attribution.

**Use:** demonstrates the OpenSky method and its limit; the decisive attribution needs the SEC/deanon ownership trace.
