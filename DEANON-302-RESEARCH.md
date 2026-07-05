# De-anonymizing the 302 jetless S&P 500 dealmakers — research + playbook

**Question:** the 302 S&P 500 firms with >$500M M&A deals that have *no* identified jet are jetless because their
aircraft register behind opaque LLCs/trusts. Can we crack them, and how deep do we have to go?

**Answer:** Most are recoverable for **free** — the obfuscation is real but the de-anonymization channels exist and
are largely public. Below: the structure taxonomy, the channels (with a previously-missed free one), the recovery
playbook, and an honest stratification of what stays unrecoverable.

---

## 1. The empirical landscape (our data)

Of 26,737 active US business jets, **57% use opaque wrappers**: 10,195 neutral LLCs, 4,219 owner-trusts (trustee),
735 tail-number-named LLCs; only 9,501 register under a corporate name. Shared registration-address clustering
exposes the obfuscation infrastructure — a handful of trustee hubs hold thousands of jets:

| Registration address | Jets | Who it is (corrected) |
|---|---|---|
| 50 S 200 E Ste 110, Salt Lake City 84111 | 1,081 | **Bank of Utah** corporate trust |
| 39 E Eagle Ridge Dr #201, N. Salt Lake 84054 | 876 | **TVPX** Aircraft Registration *(not Bank of Utah)* |
| 6440 S Millrock Dr Ste 400, SLC 84121 | 534 | **UMB Bank** aviation corporate trust |
| 1100 N Market St, Wilmington 19890 | 254 | **Wilmington Trust** (M&T) |
| 251 Little Falls Dr, Wilmington 19808 | 184 | **CSC** — Delaware registered agent (LLC shells) |

Plus **Wells Fargo Bank Northwest, N.A.** (historically the largest aircraft owner-trustee) and **Aircraft Guaranty /
Wright Brothers** (Onalaska TX / OKC — the abuse-prone foreign end, less relevant for S&P 500).

Of the 305 jetless dealmakers: **200 already have a deanon candidate jet** (HQ-address hit, opaque owner); **105 have
no candidate at all** (the NetJets/charter/no-jet floor).

## 2. The structures, and how recoverable each is

| Structure | Registry shows | True owner found via | Free? |
|---|---|---|---|
| Single-layer owner trust (Bank of Utah, Wells Fargo NW, Wilmington, TVPX, UMB) | trustee only | **trust agreement in the FAA record** names trustor/beneficiary | **Yes — CARES** |
| Non-citizen trust (post-2013) | US trustee | operating/side agreements filed since FAA 2013 NCT policy | Yes — CARES |
| Neutral / tail-named LLC ("N550LK LLC", "Notus LLC") | the LLC | FAA mailing address + SEC + registered-agent clustering | Mostly |
| LLC → trust stack | trustee → LLC | two hops; sometimes a true shell | Harder |
| Management-co / fractional (NetJets "QS", Flexjet) | the program | only in a non-FAA management contract | **No — structural** |

## 3. The channels (one was previously missed)

1. **FAA Releasable Aircraft Database** (free bulk CSV) — every N-number → registrant name+address. The backbone;
   already in hand. Owner field = the LLC/trust, *not* the operator.
2. **CARES — cares.faa.gov (the breakthrough).** The FAA digitized aircraft records: for any tail you can view/download
   the **scanned trust agreement, bill of sale, registration application — free** (account + MFA). Post-2013 trusts
   name the corporate beneficiary. This is *not* FOIA-only as we'd assumed — it makes single-layer corporate trusts
   highly recoverable at zero cost. The public Aircraft Inquiry web UI 403s scrapers; CARES + the bulk DB are the
   scalable way around it.
3. **SEC EDGAR full-text search** (`efts.sec.gov/LATEST/search-index`, free, by CIK):
   - **DEF 14A perquisite** ("personal use of company/corporate aircraft", Reg S-K Item 402, $10k threshold) →
     **confirms a jet/lift exists** for ~85–95% of operating firms. Doesn't prove ownership vs fractional.
   - **Aircraft time-sharing / dry-lease exhibits** (EX-10.x, FAR 91.501) → **name the counterparty entity**, often
     make/model, and a tail number in ~15–25% (e.g. Nike's filing names `N1972N`; Salesforce redacts).
   - **10-K Exhibit 21** → names aviation subsidiaries ("X Aviation LLC") when material.
4. **State LLC / registered-agent tracing** (OpenCorporates, DE/NV/UT SoS) — pivot tail-named LLCs on shared agent
   (CSC), formation date, and FAA mailing address. DE doesn't disclose members, so this clusters rather than names.
5. **OpenSky / ADS-B home-base** (free, we have Trino access) — confirms a candidate jet bases at the firm's home
   airport. The decisive corroborator when the registry owner is generic.

## 4. Privacy programs do **not** break our method

- **PIA** (rotating ICAO hex): breaks registry-link only, *not* position tracking. <0.1% adoption; ~69% defeated
  within 100 days via airport hand-off + call-sign + home-base + crowdsourced `plane-alert-pia.csv`.
- **LADD** (formerly BARR): blinds only the FAA SWIM feed; raw ADS-B (OpenSky/ADS-B Exchange) sees everything.
- **§803** (FAA Reauth 2024, eff. 2025-03-28): registry PII withholding, opt-in, individual; corporate applicability
  unsettled. Registry-only — does not touch ADS-B.

Net: ADS-B Out is mandatory in jet cruise airspace, so home-base detection survives all three. **>90% of US-registered
corporate jets stay position-trackable**; the untrackable residue (single-digit %) is coverage gaps + foreign reg.

## 5. The recovery playbook (free-first, escalate once)

1. **SEC EDGAR pass** across the 302 CIKs → stratify into *jet-disclosed* (perquisite) and *entity-namable*
   (time-share/Ex-21). [executed → `sec_aircraft_signals_302.csv`]
2. **FAA forward-match** the SEC-named entities + company-name/HQ-address patterns against the releasable DB.
3. **CARES** the trustee-held tails → read the trust agreement for the corporate beneficiary.
4. **OpenSky home-base** confirm each candidate bases at the firm's home airport (Trino, in hand).
5. **State/agent clustering** for the residual neutral LLCs.
6. **Escalate once (paid):** a single **JETNET or AMSTAT** subscription (phone-verified operator field) buys down the
   hard residual far cheaper than Sayari/Quandl enterprise. Only if free steps leave material gaps.

## 6. Honest stratification of the 302

- **Recoverable for free (~70–85% of the 200 with candidates):** single-layer trusts (CARES) + SEC-named entities +
  home-base confirmation. Large-cap flight departments skew recoverable.
- **Recoverable only with paid/manual effort (~10–20%):** multi-layer LLC→trust stacks, pure DE shells with commercial
  agents, redacted SEC exhibits.
- **Structurally unrecoverable (much of the 105 no-candidate firms):** NetJets/Flexjet fractional (now the #1 US
  departure category — invisible by construction), Part 135 charter, jet-card, and genuine no-jet firms. These should
  be **coded as a distinct stratum**, not imputed as missing — their non-recovery is informative (correlates with firm
  size + travel-procurement choice).

**Caveat that still binds:** even perfect jet recovery only widens *acquirer visibility*, not *target tradeability*
(most M&A targets are private). Per the project's own `WIDENED-RESULTS.md`, scaling the universe replicates the ~1.4×
within-pair effect rather than strengthening it. So this research maximizes coverage and robustness — it does not, by
itself, create new signal.

### Key sources
FAA CARES https://cares.faa.gov/ · Releasable DB https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download ·
FAA 2013 NCT policy (Fed. Reg. 2013-14434) · NBAA Owner-Trust Guide · Bank of Utah / TVPX / UMB / Wilmington Trust corporate-trust pages ·
SEC EDGAR FTS efts.sec.gov/LATEST/search-index (Reg S-K Item 402) · Nike EX-10.4 (N1972N) · Strohmeier et al., "Flying in Private Mode" (AIAA JAIS 2021), "The Real First Class?" (IEEE EuroS&P 2018) ·
FAA PIA program · NBAA LADD · FAA Reauth Act 2024 §803 (PL 118-63) · ADS-B Exchange · JETNET / AMSTAT.
