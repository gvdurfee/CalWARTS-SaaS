# Board acceptance target (intake → package)

| Field | Value |
|-------|-------|
| Product | CalWATRS Measurement Package |
| Purpose | Checklist of **Board-required export / package targets** for intake stories. What intake must eventually populate — not UX, not stack. |
| Audience | CalWATRS Product Analyst, Cursor builds, General Manager |
| Status | Domain draft for Greg sync — QI aid only |
| Date | 2026-09-23 (America/Denver) |

**CalWATRS** = California Water Accounting, Tracking, and Reporting System.  
**QI** = Qualified Individual. Use exact strings from `docs/GLOSSARY.md` in product copy.

**Hard posture:** Aid for a QI. Software drafts transforms and documents. Humans attest and submit in CalWATRS. Never auto-certify. Never invent missing meter volumes. Never scrape/submit to the portal. Never invent portal field IDs, device-type enums, or logger dialects.

**Demo A1:** Water year 2027–forward **Template Data File** shape (exact Board A1 Data headers + allowed units) with clear **prototype / not a filing** disclaimer. Not required to satisfy Water year 2025–26 **Original Data** path.

---

## 1. Template Data File — A1 (Diversion to Direct Use)

**Data headers (exact; do not rename, add, or delete):**  
`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_USE`, `VOLUME_UNIT`, `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE`

| Target | Rule |
|--------|------|
| One file ↔ one **claimed water right** | Board Manual App. A.4 / CCR Tit. 23 §935(a)(1)(B) |
| `DATE` | `YYYY-MM-DD` |
| `TIME` | `hh:mm:ss` or `hh:mm:ss -n` |
| `FLOW_RATE` | Numbers only; **no negatives**. How-to: instantaneous |
| `FLOW_RATE_UNIT` | Exactly one of: `CUBIC FEET PER SECOND`, `GALLONS PER MINUTE` (consistent in file) |
| `VOLUME_DIVERTED_TO_USE` | Numbers only; **no negatives**. How-to: cumulative since last measured value |
| `VOLUME_UNIT` | Exactly one of: `GALLONS`, `ACRE-FEET` (consistent in file) |
| Optional columns (How-to) | `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE` |
| `REDIVERSION_STATUS` values | `yes` or `no` (when filled) |

**OPEN:** Whether right identity is carried only by CalWATRS upload context vs filled `WATER_RIGHT` column (optional in template; one-file-per-right still required).  
**OPEN:** Exact QI confirmation of “cumulative since last measured value” semantics for every method (see PRD open Q7).

**Source:** `calwatrs-sources/template-a1.xlsx` Data + How to use; GLOSSARY A1 / column headers.

---

## 2. Template Data File — A2 (Diversion to Storage)

**Data headers (exact):**  
`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_STORAGE`, `VOLUME_UNIT`, `WATER_RIGHT`, `PLACE_OF_STORAGE`, `REDVERSION_STATUS`

| Target | Rule |
|--------|------|
| Same date/time/unit/no-negative rules as A1 | |
| `VOLUME_DIVERTED_TO_STORAGE` | How-to: instantaneous measurement |
| Optional (How-to) | `WATER_RIGHT`, `PLACE_OF_STORAGE`, rediversion field |
| Rediversion **Data** header | Must export `REDVERSION_STATUS` (Board Data spelling; How-to lists `REDIVERSION_STATUS`) |

**OPEN:** Which spelling validators accept (`REDVERSION_STATUS` vs `REDIVERSION_STATUS`). Match **Data** sheet until Board republishes.  
**OPEN:** Same right-identity / volume-semantics questions as A1.

**Source:** `calwatrs-sources/template-a2.xlsx`; GLOSSARY; PRD hard rule 12.

---

## 3. Annual-report upload slots (packaging concepts)

| Slot | Water year 2025–26 | Water year 2027+ | Product expectation |
|------|--------------------|------------------|---------------------|
| **Template Data File** | Optional | **Required** (“Only files based on the provided templates will be accepted”) | Demo / primary export target = Board-shaped A1/A2 |
| **Original Data** | **Required** | Optional (raw/other formats) | Always retain immutable raw / Original Data archive |
| **Supplemental Files** | Optional | Optional | Calibration, conversion formulas, explanations |

Do **not** collapse these three into one vague “upload” in copy or acceptance tests.

**OPEN:** Exact CalWATRS UI control labels / field IDs for these slots — unknown; use the three Board names above.

**Source:** *Submitting Measurement Data in CalWATRS* (Nov 19, 2025); GLOSSARY Original Data / Template Data File.

---

## 4. Measurement methodology draft — CCR Tit. 23 §934(a)

UI label: **Methodology draft** only. Never “certified.” QI certification is human (§934(a)(10)); software does not perform it.

Content blocks intake / export must eventually support (as applicable):

| # | Content that must appear somewhere in the package |
|---|---------------------------------------------------|
| 1 | Name/contact (email) for participants; primary contact; **QI who certified** (human-supplied for attestation) |
| 2 | Identification number of each **claimed water right** covered |
| 3 | Each **Point of Diversion** + each measurement location and **measurement device** |
| 4 | Any **quality assurance** protocol |
| 5 | Conversion method/formula if device does not directly measure both discrete volume and rate |
| 6 | Method to aggregate hourly+ data to daily values |
| 7 | Method to distinguish direct diversion vs storage vs withdrawal/release/rediversion if not measured individually |
| 8 | Method to distinguish and **apportion** general measurement data to each claimed water right |
| 9 | Any other description deriving submitted data (§935) from **raw device output** |
| 10 | **Certification by a QI** — product produces draft only; never auto-complete as certified |

**Device registry** fields to help QI enter in CalWATRS (§934(b); free text until Board enums captured): make/model; type class; location/POD; recording device if different; measured parameter/units of raw output; accuracy; installation date; QI contact who installed/verified.

**OPEN:** Exact CalWATRS methodology form control labels / field IDs — use §934(a) headings until captured.  
**OPEN:** Device-type dropdown enums — unknown; free text in v1.  
**OPEN:** Whether methodology files outside the annual-report session — Board says through CalWATRS; tile set by demo date unknown.

**Source:** Approved Ch. 2.8 clean copy §934; GLOSSARY Measurement methodology / Methodology draft / Device registry; ISOR (QI certify, not necessarily prepare).

---

## 5. Filing checklist + audit trail

| Artifact | Acceptance target |
|----------|-------------------|
| **Filing checklist** | Human checklist of what to upload/enter in CalWATRS for the water year / right(s). Not a portal bot. |
| **Audit trail** / **Audit log** | Append-only lineage: every raw byte (and any PDF/photo if later allowed) → map/method/QA/apportionment → each exported rate/volume cell; zero-fill only after explicit logged confirmation |

**Intake implication (Domain):** Structured time series may populate A1/A2 numeric cells after documented method + QI-facing confirmation. OCR / PDF / camera must not silently invent `FLOW_RATE` or volume cells — treat as evidence until explicit acceptance is logged (or keep out of Template Data File path in early slices).

---

## 6. Pass/fail for “Board-shaped package” (acceptance)

- [ ] A1 and/or A2 **Data** headers match Board templates exactly (incl. A2 `REDVERSION_STATUS`).
- [ ] Units and date/time strings match allowed Board enums/formats; no negatives.
- [ ] One Template Data File per **claimed water right**; shared-meter **apportionment** sums to 100% before export (when that path is in scope).
- [ ] Export pack can include: Template Data File(s) + **Methodology draft** + **Filing checklist** + **Audit trail**; Original Data / raw retained.
- [ ] Copy never claims software certified compliance, completed a CalWATRS filing, or invented volumes.
- [ ] Demo outputs labeled **prototype / demo / not a filing**.

---

## 7. Out of this acceptance target (v1)

Templates B/C/D; large-diversion weekly automation; full ACP workflows; portal scrape/submit; meters/SCADA as product; other states; legal opinions; invented portal field IDs.

---

## Sources

- `docs/GLOSSARY.md`, `docs/PRD.md`, `docs/FIRST_SLICE.md`
- `calwatrs-sources/template-a1.xlsx`, `template-a2.xlsx`
- Board: *Submitting Measurement Data in CalWATRS*; Measurement and Reporting Manual 2026; CCR Tit. 23 Ch. 2.8 §934–§935 (approved clean copy); Water Measurement Regulation program materials

**Suggested path in pack:** `docs/BOARD_ACCEPTANCE_TARGET.md`
