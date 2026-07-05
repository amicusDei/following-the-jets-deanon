# newfirm_deals_geocoded.csv — priority missing deals joined to researched HQ coords

**What:** The priority missing-HQ deals (>$100M) joined to their web-researched HQ coordinates. One row = one deal-with-coords.

**Columns:** `acq` · `tgt` · `tpublic` · `deal_value` · `dateann` · `priority` (P1_>500M / P2_100-500M) · `target` · `hq_city` · `hq_country` · `lat`/`lon` · `confidence` · `note`.

**Source:** join of `targets_missing_hq.csv` ⨯ `target_hq_research.csv`. **Note:** 160 deal-rows, 129 now geocodable (HIGH/MED with coordinates).

**Use:** the newly-testable deals — acquirer jet now trackable (in `dealmaker_jets.csv`) and target HQ now located.
