# sec_entity_namable_shortlist.csv — firms whose SEC filings name an aircraft entity (35 firms)

**What:** The subset of jetless dealmakers whose SEC filings name an aircraft entity (time-sharing exhibit or Exhibit-21 aviation subsidiary) — the forward-match targets. One row = one firm.

**Columns:** as `sec_aircraft_signals_302.csv` plus `ts` (timeshare count, clipped ≥0) and `ex` (ex21 count, clipped ≥0).

**Source:** filtered from `sec_aircraft_signals_302.csv` where `entity_namable`. **Examples:** Bristol-Myers (11 time-share exhibits), Salesforce (13), Blackstone (47), ICE (33), Morgan Stanley (25), Visa (50), Cardinal Health (78), Bank of America (62).

**Use:** input to the SEC-document extraction (`sec_extracted_aircraft.csv`) that pulls actual tail numbers.
