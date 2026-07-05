# faa_jet_pull_summary.about.md — per-firm status of the FAA registry pull

**What:** Per-firm outcome of the FAA name-match jet pull across the 299 jetless targets. One row = one firm.

**Columns:** `ticker` · `firm` · `total_musd` · `n_jets` (AND-match jets found) · `n_in_hq_state` (subset confirmed in HQ state) · `note` · `status` (`identified` / `needs_flightdata` / `name_too_generic`).

**Source:** FAA Releasable Aircraft Database matching summary.

**Use:** triage — which firms the registry resolved vs which were handed off to the OpenSky/SEC pipeline because their name is too generic or their jets sit behind opaque LLCs.
