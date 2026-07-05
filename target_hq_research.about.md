# target_hq_research.csv / .json — web-researched deal-target HQ coordinates (154 targets)

**What:** Headquarters coordinates for M&A deal targets that lacked geocoding, gathered by deep web research. One row = one target company. CSV and JSON hold the same records.

**Columns:** `target` (SDC target name, copied exactly) · `hq_city` · `hq_country` · `lat`/`lon` (decimal degrees, null for asset-portfolios) · `confidence` (HIGH/MED/LOW) · `note`.

**Source:** 7 web-research agents (corporate filings, press, planespotters, etc.). **Coverage:** 142 with coordinates (102 HIGH, 21 MED); 12 asset-portfolios with no single HQ (`asset_or_unit_no_single_hq`). **Examples:** VMware→Palo Alto, Red Hat→Raleigh, Cerner→North Kansas City, GOJO→Akron, Tink→Stockholm.

**Use:** geocodes the deal targets so jet→target-HQ visits can be computed; lifted 82-firm deal coverage 180→328.
