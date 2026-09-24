# CalWATRS Measurement Package — PRD v1

| Field | Value |
|-------|-------|
| Product | CalWATRS Measurement Package |
| Version | 1 |
| Date | 2026-09-23 (America/Denver) |
| Status | Ready for first-slice implementation handoff |
| Scope lock | A1 (Diversion to Direct Use) and A2 (Diversion to Storage) only |

This document is version 1 only. It is an engineering product requirements document. Do not invent a technology stack, login system, or features not listed here.

---

## 1. Users

### Primary user (first buyer)

Water-rights consultant, Professional Engineer (P.E.), or hydrographer who prepares measurement packages for many claimed water rights each January.

**Job:** Turn client logger / device time series into Board-ready A1 and/or A2 Template Data Files, a measurement methodology draft the Qualified Individual (QI) will stand behind, a filing checklist, and an audit trail — without inventing volumes or auto-certifying compliance.

### Secondary user (later; not first slice)

Ranch / vineyard / district staff who prepare a package for their own right(s), often after AB 589 QI training.

### Not a user of this product

- State Water Resources Control Board (they own CalWATRS portal)
- Meter OEMs as customers (possible partners later)

### Product posture

Aid for a Qualified Individual. Software drafts transforms and documents. Humans attest and submit in CalWATRS. Never auto-certify. Never invent missing meter volumes.

---

## 2. Screens (v1 product; first slice is a subset — see docs/FIRST_SLICE.md)

Exact layout and navigation are open (see Open questions). Required capabilities by screen:

0. **Landing page + what-if demo** (earliest *visible* deliverable; see `docs/FIRST_SLICE.md` Demo slice)  
   Public/prototype page: sample mid-size ag diversion scenario; visitor adjusts a few measurements; downloads correctly headed A1 CSV; plain-language summary; clear demo/not-a-filing labeling. Not the full product.

1. **Client / right / device registry**  
   Enter and edit: client, claimed water right, Point of Diversion (POD), measurement device, water year, template type (A1 and/or A2), Board Measurement Device ID when known, install/calibration dates.

2. **Ingest**  
   Upload logger CSV/Excel; map columns to timestamp + raw reading + unit; link batch to a device; show validation errors; keep raw file immutable.

3. **Method**  
   Choose a conversion method and parameters; produce time-aligned flow rate and volume series; write every transform to the audit log.

4. **QA / QC**  
   Water-year window (Oct 1 – Sep 30), unit conversion to allowed enums, gap flags, optional zero-fill only after explicit user confirmation (logged).

5. **Apportionment** (shared meter)  
   Split one physical series across claimed rights; fractions or acreage keys must sum to 100%; emit one Template Data File per right.

6. **Export pack**  
   Download: A1/A2 `.xlsx` (Board Data headers exact), methodology draft, filing checklist, audit log. No CalWATRS portal submit.

7. **Batch / consultant list** (thin; after single-right path works)  
   Multi-client / multi-right list and zip of packs.

---

## 3. Stored data

Minimum entities (storage technology open):

| Entity | Required fields (content) |
|--------|---------------------------|
| Client | Name; optional contact notes |
| Water right | Identifier / claim label; client link; template type(s) A1 and/or A2 |
| Point of Diversion | Label; link to right(s); location notes as free text |
| Measurement device | Nickname; make/type free text until Board enum list known; install date; last calibration date; Board Measurement Device ID (e.g. `M0xxxxx`) when pasted by user |
| Water year | Start Oct 1 / end Sep 30; year label (e.g. WY2026) |
| Ingest batch | Device link; original filename; raw bytes; upload time; column map; validation report |
| Method run | Method id; parameters; input batch id(s); output series id; QI confirmation flags where required |
| Series (raw and derived) | Timestamps; values; units; lineage to batch/method |
| Apportionment plan | Source series; right → share keys; must validate sum 100% |
| Export artifact | Right; template type; file bytes or path; schema version / Board template hash; created time |
| Audit event | Append-only: who/what/when; formula or rule; inputs; outputs |

Retention expectation to surface in UI copy: keep Original Data / raw archive suitable for long Board retention expectations (commonly discussed as ~10 years) — exact policy open.

---

## 4. Business rules

### Hard rules

1. One Template Data File represents **one claimed water right** only (Board Manual Appendix A.4).
2. Shared meters require an explicit apportionment method; shares must sum to **100%** before export (block export otherwise).
3. Do **not** modify, delete, or add columns on Board templates. Exporter must match the **Data** sheet headers of the Board `.xlsx`.
4. No negative `FLOW_RATE` or volume values.
5. `DATE` = `YYYY-MM-DD`. `TIME` = `hh:mm:ss` or `hh:mm:ss -n`.
6. Flow units (exact strings): `CUBIC FEET PER SECOND` or `GALLONS PER MINUTE` — one unit consistent per file.
7. Volume units (exact strings): `GALLONS` or `ACRE-FEET` — one unit consistent per file.
8. Zero-fill of gaps only after explicit user confirmation; log the confirmation.
9. Do not invent volumes the meter never produced.
10. Do not auto-certify QI / compliance; drafts only.
11. Do not scrape or auto-submit to the CalWATRS portal.
12. **A2 Data header caveat:** Data sheet uses `REDVERSION_STATUS` (missing “I”); How-to-use lists `REDIVERSION_STATUS`. Exporter **must** match the **Data** sheet until the Board republishes.
13. Raw ingest bytes are immutable; transforms are append-only lineage.
14. Every exported volume/rate cell must be traceable in the audit log.

### A1 Data columns (verified from Board `template-a1.xlsx` Data sheet)

`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_USE`, `VOLUME_UNIT`, `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE`

Optional per Board How-to-use: `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE`.

### A2 Data columns (verified from Board `template-a2.xlsx` Data sheet)

`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_STORAGE`, `VOLUME_UNIT`, `WATER_RIGHT`, `PLACE_OF_STORAGE`, `REDVERSION_STATUS`

Optional per Board How-to-use: `WATER_RIGHT`, `PLACE_OF_STORAGE`, rediversion field (export using Data header spelling `REDVERSION_STATUS`).

### Method library v1 (allowed methods)

| Method | Purpose | Limits |
|--------|---------|--------|
| Totalizer / flow meter integration | Pulse or volume factor → interval volume + rate | Document pulse/factor units in audit + methodology |
| Stage → storage curve | User curve points (stage, volume) | Mass-balance evaporation **out of scope** |
| Pump runtime × rated flow | Runtime × rated flow | Document limits; QI must confirm suitability; energy/kWh curve later |

### Deadline spine (context for “done when”; not features)

- Oct 1, 2026: updated rules begin; existing methods/ACPs expire on Board timeline.
- Jan 31, 2027: WY2026 report + Original Data; device registry; measurement methodology.
- Jan 31, 2028: first annual report that requires Template Data Files for required data.

### Build order (locked for implementation after first slice)

**M1 → M8(thin) → M2 → M3 → M5 → M4 → M6 → M7**

First slice (see `docs/FIRST_SLICE.md`) is a vertical stub that proves ingest → one method → A1 export + audit, not the full M1–M8 product.

---

## 5. Out of scope (v1)

- Replace CalWATRS portal; scrape or auto-submit filings
- Sell / install meters as the core product
- Templates B / C / D (large storage >5,000 AF packages)
- Native SCADA / device firmware connectors beyond CSV/Excel ingest
- Other states’ measurement rules
- Full Alternative Compliance Plan (ACP) workflows
- Large-diversion weekly posting / telemetry automation
- Water-rights adjudication, priority, curtailment legal advice
- Auto QI certification or legal opinion engine
- Inventing missing data to fill templates
- Login / multi-tenant SaaS billing / SSO (not decided — do not build unless listed later)
- Hard-coding WY2026 frequency tables as permanent WY2027+ law (Board guidance pending)

---

## 6. Done when (v1 product acceptance)

Pass/fail:

1. Consultant can complete **raw CSV → right-apportioned A1 and/or A2 files + methodology draft + filing checklist + audit log** for at least one **multi-right shared-meter** scenario.
2. Export headers match Board A1/A2 **Data** sheets exactly (including A2 `REDVERSION_STATUS`).
3. Apportionment shares sum to 100% or export is blocked.
4. No silent overwrite of raw series.
5. Transform log covers every derived volume/rate cell exported.
6. Methodology draft covers CCR title 23 §934(a)(1)–(10) **content blocks** (narrative outline; portal form control names may be unknown).
7. Unit enums and date/time formats match Board How-to-use rules above.
8. Product copy never claims the software certified compliance.

First-slice done-when is narrower — see `docs/FIRST_SLICE.md`.

Demo-slice done-when (landing + what-if A1 CSV) is narrower still and may ship first — see Demo slice in `docs/FIRST_SLICE.md`.

---

## 7. Open questions

1. Application stack, repo host, and packaging (desktop vs web vs CLI) — **repo host is Cursor Origin** (private git). The demo is a static page. The full application stack is still **not decided.**
2. Authentication / multi-user login — **not decided; do not invent.**
3. Persistence technology (files only vs local DB vs server) — **not decided.**
4. Exact CalWATRS portal methodology form field IDs / labels — content from §934(a) known; UI schema **unknown**.
5. Full device-type dropdown enums from live CalWATRS registry UI — **unknown**; use free text until captured.
6. Logger CSV dialects to ship as named profiles — **unknown** until consultant interviews; ship configurable column mapping first.
7. Whether A1 `VOLUME_DIVERTED_TO_USE` is always treated as “cumulative since last” vs A2 volume “instantaneous” wording in How-to-use — implement with explicit method documentation; confirm with QI interviews.
8. Pricing, packaging, and commercial SKU — out of engineering PRD.
9. Where Board template files are vendored in-repo and how schema version/hash is recorded — **decide at implementation.**
10. PDF/DOCX toolchain for methodology and checklist — **not decided.**
11. Demo / landing-page hosting (local-only vs public URL vs password gate) — **Vercel hosts the static demo** (`demo/`). A password gate remains **not decided.** The local page still runs without Vercel.
12. Demo sample data: keep fictional fixtures vs later anonymized partner data — **default fictional until decided.**
13. Whether the public demo is static (client-side only) or needs a backend — **not decided; prefer simplest path that preserves A1 header fidelity.**

---

## Sources (do not invent beyond these)

Board A1/A2 templates (local copies under project `calwatrs-sources/`), Measurement and Reporting Manual 2026 update, Submitting Measurement Data fact sheet, CCR title 23 §934, Resolution 2025-0037 / related Board materials, prior Market Researcher packs. Prefer verified `.xlsx` Data headers over older markdown maps if they disagree.
