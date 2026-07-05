# deanon_attribution.csv — deanon scoring of the OpenSky-confirmed shortlists

**What:** The project's deanon signals applied to the home-base-confirmed prototype jets, to attribute ownership. One row = one confirmed-based candidate.

**Columns:** `ticker` · `N` (tail) · `NAME` (FAA owner) · `MODEL` · `n_flights` · `home_base`/`home_share` · `rcity`/`rzip` (registration city/ZIP) · `owner_kind` (company_named/named_trustee/opaque_llc) · `vanity` (tail encodes firm) · `street_match` (registered at firm HQ address/ZIP) · `deanon_verdict` (STRONG/MEDIUM/BASED_ONLY_ambiguous).

**Source:** deanon scoring (`deanon/deanon_review.py` logic) over FAA registration + firm HQ. **Finding:** only Broadcom `N901MM` scored STRONG (HQ-ZIP); MSFT/NVDA/BMS register at neutral hangar/FBO addresses → 0 — they need FOIA'd CARES trust docs.

**Use:** shows the free deanon funnel's ceiling on deliberately-opaque mega-caps.
