# dealmaker_flight_activity.csv — flight activity of the dealmaker jets (204k flights)

**What:** All reconstructed flights, 2018–present, for the jets in `dealmaker_jets.csv`. One row = one flight segment. **(Gitignored — bulky/reproducible; lives on disk only.)**

**Columns:** `icao24` · `callsign` · `firstseen`/`lastseen` (Unix UTC) · `day` (epoch partition) · `dep_airport`/`arr_airport` (ICAO) · `firm_id` · `ticker` · `name`.

**Source:** OpenSky Trino `flights_data4` via `pyopensky` (partition-safe `day` filter), pulled per the icao24 set. ~204,024 rows / 198 jets / 108 firms.

**Use:** the raw flight panel for the dealmaker jets; reproduce with `pull_dealmaker_flights.py` + `dealmaker_jets.csv`. Timestamps UTC; OpenSky coverage grows over time.
