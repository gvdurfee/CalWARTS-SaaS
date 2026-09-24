# CalWATRS Measurement Package — First slice

## Goal

Prove the product with the **smallest** vertical path:

**one client → one claimed water right → one measurement device → one CSV ingest → one totalizer method run → one A1 Template Data File + audit log**

Stop for human review. Do not build login, apportionment, A2, methodology PDF, checklist, or consultant batch in this slice unless listed below as explicit deliverables.

**Also see Demo slice below** — landing page + what-if A1 CSV is the earliest *visible* deliverable and may ship before the full vertical path.


## Demo slice (earliest visible deliverable)

**Sequence:** build this **before or alongside** the full first-slice path above. It is the smallest path that proves the concept **to a consultant visitor**, not the full product path.

### Goal

Ship a **landing page** plus an **interactive what-if demo** that a water-rights consultant recognizes in under two minutes.

### Demo behavior

1. **Scenario (realistic, fictional):** Mid-size agricultural diversion, e.g. “North Ditch – Sample Ranch,” one registered measuring device, A1 Diversion to Direct Use. Use fictional rights/device IDs clearly labeled as sample/demo (do not present as a real Board filing).
2. **Visitor inputs:** Adjust a small set of sample measurements (e.g. a few DATE/TIME rows, FLOW_RATE and/or interval volume, units). Pre-fill with realistic defaults so the page works with zero typing.
3. **Outputs:**
   - Downloadable **A1 CSV** whose header row is exactly:  
     `DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_USE`, `VOLUME_UNIT`, `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE`  
     (verified Board A1 Data sheet; same columns as `calwatrs-sources/template-a1.xlsx`).
   - Short **plain-language summary** of what was produced (row count, water right label, units, that this is demo output).
4. **Prototype labeling:** Landing page and demo UI must state this is a **prototype / demo**, not the full CalWATRS Measurement Package, and does not submit to CalWATRS or certify compliance.

### Demo done when

- [x] Landing page explains the product job in plain language (logger → Board-ready A1 pack aid for a Qualified Individual).
- [x] What-if controls change the CSV output deterministically.
- [x] CSV header matches the Board A1 Data columns exactly (automated check preferred).
- [x] No negative flow/volume in demo output.
- [x] Units use allowed Board strings only (`CUBIC FEET PER SECOND` or `GALLONS PER MINUTE`; `GALLONS` or `ACRE-FEET`).
- [x] Visible “demo / not a filing” disclaimer.
- [x] Agent stops for review after demo works — do not expand into auth, portal submit, A2, or apportionment unless asked.

### Demo out of scope

- Real CalWATRS login or upload automation
- Real client PII or real Board device IDs
- Full registry, methodology draft, checklist, audit-log product UI (those belong to the main first slice / later slices)
- Inventing a stack beyond what Open questions allow

### Relationship to main first slice

| Track | Proves | Audience |
|-------|--------|----------|
| **Demo slice** | Consultant can see/feel A1-shaped output from sample inputs | Visitors / early design partners |
| **Main first slice** | Internal vertical: ingest → totalizer → A1 file + audit log | Implementers / QI workflow |

Prefer shipping the demo first if only one track can run. Shared A1 header constants and sample scenario fixtures should be reused by both tracks when the main slice is built.


## In scope

1. Local project scaffold only as needed to run the slice (stack is an Open question — if unset, prefer the simplest local toolpath already present in the repo; **do not invent** a cloud login stack).
2. Minimal registry records for the sample below (file- or DB-backed — Open question).
3. CSV ingest with column mapping UI or config for the sample dialect.
4. Totalizer method: apply a pulse/volume factor to produce interval `FLOW_RATE` and `VOLUME_DIVERTED_TO_USE`.
5. Export one A1 `.xlsx` whose **Data** sheet headers match the Board template exactly.
6. Append-only audit log covering ingest map, factor, and each derived output row lineage at method level (row-level or batch-level with replayable parameters).
7. Fixture sample data committed under `fixtures/first-slice/` (or equivalent).

## Out of scope (this slice)

- Authentication / users / multi-tenant
- A2 export
- Shared-meter apportionment
- Stage-storage and pump runtime methods
- Methodology draft document and filing checklist
- CalWATRS portal integration
- Templates B/C/D
- Consultant multi-right zip batch
- Polished design system

## Sample records

Use these exact fixture identities so review is deterministic.

### Client

| Field | Value |
|-------|-------|
| Name | Sample Irrigation Client |

### Claimed water right

| Field | Value |
|-------|-------|
| Label | SAMPLE-WR-001 |
| Template type | A1 |

### Point of Diversion

| Field | Value |
|-------|-------|
| Label | POD North Ditch |

### Measurement device

| Field | Value |
|-------|-------|
| Nickname | North ditch magnetic meter |
| Board Measurement Device ID | M0SAMPLE1 |
| Notes | Fixture only — not a real Board id |

### Water year

| Field | Value |
|-------|-------|
| Label | Water year 2026 |
| Start | 2025-10-01 |
| End | 2026-09-30 |

### Method parameters

| Field | Value |
|-------|-------|
| Method | Totalizer |
| Volume per pulse | 10 |
| Pulse volume unit | GALLONS |
| Output volume unit | GALLONS |
| Output flow unit | GALLONS PER MINUTE |

### Sample CSV (`fixtures/first-slice/sample-logger.csv`)

```csv
timestamp,pulses
2025-10-01T00:00:00,0
2025-10-01T01:00:00,60
2025-10-01T02:00:00,60
2025-10-01T03:00:00,0
```

Interpretation for the slice: each row’s `pulses` is pulses counted in the interval ending at `timestamp` (document this assumption in the audit log). Interval volume = `pulses * 10` gallons. Derive an interval flow rate consistent with that volume over the interval length; document the formula in the audit log. Do not invent extra rows beyond what the method derives.

### Expected A1 Data headers (exact)

`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_USE`, `VOLUME_UNIT`, `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE`

Optional columns may be blank or filled with fixture defaults:

| Column | Fixture default |
|--------|-----------------|
| BENEFICIAL_USE | irrigation |
| WATER_RIGHT | SAMPLE-WR-001 |
| REDIVERSION_STATUS | no |
| PLACE_OF_USE | North field |
| FLOW_RATE_UNIT | GALLONS PER MINUTE |
| VOLUME_UNIT | GALLONS |

Vendor the Board A1 template from `calwatrs-sources/template-a1.xlsx` (or repo copy) and write the Data sheet only.

## Files the coding agent should create first

Create only what the slice needs. Suggested paths (adjust if the chosen stack requires different layout; record the choice under Open questions if you must diverge):

```
docs/PRD.md                 # already provided — do not rewrite scope
docs/GLOSSARY.md            # already provided
docs/FIRST_SLICE.md         # already provided
.cursor/skills/calwatrs-first-slice/SKILL.md  # already provided

fixtures/first-slice/sample-logger.csv
fixtures/first-slice/expected-a1-headers.json
fixtures/first-slice/README.md   # formula + assumptions

# application (names illustrative — stack open)
README.md                    # how to run the first slice only
<stack-appropriate source for registry + ingest + totalizer + a1 export>
<stack-appropriate audit log writer>
tests/ or equivalent proving: headers match; no negative values; audit log exists after export
```

Do **not** create B/C/D exporters, auth modules, or portal clients in this slice.

## Done when (first slice)

1. Given the sample CSV and parameters above, the tool produces an A1 `.xlsx` with correct Data headers.
2. No negative flow or volume values.
3. Units use allowed Board strings only.
4. Audit log records method parameters and that raw input was retained.
5. Automated test or script checks header equality against the Board A1 Data header list.
6. Agent stops and reports how to run the demo — no scope expansion.

## Open questions

4. Demo hosting (static page, local only, or shared URL) — **Vercel hosts the static page** in `demo/`. Local open of `demo/index.html` still works. A password gate is still **not decided.**
5. Whether demo sample data stays fictional forever or is later replaced by anonymized real partner data — **not decided; default fictional.**
6. Whether demo downloads CSV only or also offers Board-shaped `.xlsx` — CSV is required for this demo slice; xlsx optional later.

1. Stack and app shape (CLI vs local web vs desktop) — not decided.
2. Whether interval pulse semantics match the logger brand target customers use — confirm in interviews; document assumption for the fixture.
3. Whether to fill optional A1 columns in the fixture export or leave blank — default fill as table above unless product owner says blank.
