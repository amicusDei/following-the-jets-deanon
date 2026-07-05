# targets_missing_hq.csv — jet-firm deal targets lacking HQ coords (round 1)

**What:** Deal targets of the jet-firms that had no HQ coordinates in any source — the web-research worklist (priority pass). One row = one missing deal.

**Columns:** `acq` (acquirer) · `tgt` (target) · `tpublic` · `deal_value` ($M) · `dateann` · `priority` (`P1_>500M` / `P2_100-500M` / blank).

**Source:** `jetfirm_all_deals_82.csv` minus targets already geocoded (backtest_wide.targets + project private-HQ research + deals.csv). **Note:** 883 deal-rows missing at round 1; 158 priority (>$100M) → researched into `target_hq_research.csv`.

**Use:** the input list that drove the target-HQ web research.
