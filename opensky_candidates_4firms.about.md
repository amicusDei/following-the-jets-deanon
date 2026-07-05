# opensky_candidates_4firms.csv — FAA candidate jets for the 4 prototype firms (70 jets)

**What:** Large-cabin business jets registered to neutral LLCs in the home-airport metro of the four opaque prototype firms (BMY, MSFT, NVDA, AVGO). One row = one candidate jet. **Candidates only** — ownership not yet attributed.

**Columns:** `ticker` · `home` (home airport ICAO) · `N` (tail) · `hex` (icao24) · `NAME` (FAA owner) · `CITY`/`STATE` · `MFR`/`MODEL`.

**Source:** FAA Releasable Aircraft Database, filtered to large-cabin (Gulfstream/Bombardier/Falcon/Embraer) neutral-LLC jets in each firm's HQ metro. **Caveat:** NVDA and AVGO produce the *identical* KSJC pool — registry geography can't separate co-located firms.

**Use:** the candidate shortlist that the OpenSky home-base step (`opensky_confirmed.csv`) filters.
