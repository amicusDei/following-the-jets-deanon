# cohort_validation.csv — recall validation on the 269 known cohort jets

**What:** The identification method run against ground truth (the 269 known business jets of the 133-firm cohort) to measure recall. One row = one known business jet.

**Columns:** `icao24` · `tail` · `firm_id` · `name` · `ticker` · `owner` (FAA) · `owner_kind` · `vanity` · `zipmatch` (registered at firm HQ ZIP) · `jet_home` (modal airport) · `home_ok` (bases in firm top-3 airports) · `deanon_strong` (any deanon signal fires).

**Source:** `jets.csv` + `flights_business.csv` + FAA registration. **Finding:** home-base recall ~72% (86% among jets with flight coverage); deanon scores 100% but that's **selection bias** — the cohort is the openly-registered subset (80% company-named, 48% at HQ-ZIP), so it can't estimate recall on opaque firms.

**Use:** the honesty check — even for trusted firms the method captures ~72% of jets, and cohort success doesn't generalize to opaque mega-caps.
