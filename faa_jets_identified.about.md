# faa_jets_identified.csv — FAA name-match candidates (broad, needs vetting)

**What:** Business jets matched to jetless dealmakers by **AND-logic owner-name matching** in the FAA registry (every distinctive company token present in the registered owner name). One row = one candidate jet. Includes false positives (namesakes) — for manual vetting.

**Columns:** `ticker` · `firm` · `N` (tail) · `hex` (icao24) · `NAME` (FAA owner) · `CITY`/`STATE` · `hq_state` · `state_match` (owner state == HQ state) · `MFR`/`MODEL`.

**Source:** FAA Releasable Aircraft Database (active business jets) ⨯ firm names. **Caveat:** ~962 rows, low precision — single-token firms leak namesakes. The vetted subset is `faa_jets_highconf.csv`.

**Use:** raw candidate pool; the registry pass that showed name-matching only reliably works for distinctively-named firms.
