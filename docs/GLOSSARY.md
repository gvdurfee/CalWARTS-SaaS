# CalWATRS Measurement Package — Glossary (UI and docs wording)

Use these exact strings in user-visible UI, exports notes, and agent-written docs unless an Open question says the Board portal label is still unknown.

| Term | Exact words to use | Meaning / notes |
|------|--------------------|-----------------|
| CalWATRS | CalWATRS | State Water Resources Control Board portal for water rights measurement reporting. Do not style as “CalWatrs” or “calwatrs” in UI. |
| State Water Resources Control Board | State Water Resources Control Board | Prefer full name on first use in a screen; “Board” is allowed afterward. |
| Board | Board | Short form after first full name in the same view. |
| A1 | A1 | Template **A1 — Diversion to Direct Use**. UI short label: `A1`. |
| A2 | A2 | Template **A2 — Diversion to Storage**. UI short label: `A2`. |
| Diversion to Direct Use | Diversion to Direct Use | Long name for A1 when a subtitle is needed. |
| Diversion to Storage | Diversion to Storage | Long name for A2 when a subtitle is needed. |
| Template Data File | Template Data File | Board-format measurement file for a single claimed water right. |
| Original Data | Original Data | Non-template logger/device upload accepted for earlier water years; still retain always. |
| Water year | Water year | October 1 through September 30. UI example: `Water year 2026` or `WY2026` (both allowed; prefer `Water year 2026` in forms). |
| Claimed water right | Claimed water right | The right/claim the Template Data File represents. One file → one claimed water right. |
| Water right | Water right | Allowed short label on fields that map to column `WATER_RIGHT`. |
| Point of Diversion | Point of Diversion | Intake location. Abbreviation `POD` allowed in dense tables after first full use on the screen. |
| POD | POD | Abbreviation for Point of Diversion. |
| Place of Use | Place of Use | Maps to A1 column `PLACE_OF_USE`. |
| Place of Storage | Place of Storage | Maps to A2 column `PLACE_OF_STORAGE`. |
| Beneficial use | Beneficial use | Maps to A1 column `BENEFICIAL_USE` (optional). |
| Measurement device | Measurement device | Physical meter/logger/sensor used for the diversion. |
| Measurement Device ID | Measurement Device ID | Board-assigned id when known (example pattern `M0xxxxx`). User pastes; software does not invent. |
| Device registry | Device registry | Board requirement to register measurement devices in CalWATRS; this product stores local fields to help the QI enter them. |
| Qualified Individual | Qualified Individual | Person who may certify measurement methodology / accuracy under Board rules. Abbreviation `QI` after first use on the screen. |
| QI | QI | Abbreviation for Qualified Individual. |
| Measurement methodology | Measurement methodology | Narrative/package content required under CCR title 23 §934(a). Product produces a **draft** only. |
| Methodology draft | Methodology draft | UI label for the editable §934(a) narrative export. Never label it “certified.” |
| Filing checklist | Filing checklist | Checklist of what to upload/enter in CalWATRS. Not a portal bot. |
| Audit trail | Audit trail | Append-only log of transforms and user confirmations. Same idea as “audit log.” |
| Audit log | Audit log | Allowed synonym for Audit trail in UI. |
| Apportionment | Apportionment | Split of one shared meter series across claimed water rights. |
| Shared meter | Shared meter | One device serving more than one claimed water right. |
| Totalizer | Totalizer | Method: meter/totalizer pulses or volume factor → interval volume and rate. |
| Stage-storage curve | Stage-storage curve | Method: stage → volume via user curve points. |
| Pump runtime method | Pump runtime method | Method: runtime × rated flow (QI must confirm suitability). |
| Flow rate | Flow rate | Column `FLOW_RATE`. |
| Flow rate unit | Flow rate unit | Column `FLOW_RATE_UNIT`. Allowed values only: `CUBIC FEET PER SECOND`, `GALLONS PER MINUTE`. |
| Volume diverted to use | Volume diverted to use | A1 column `VOLUME_DIVERTED_TO_USE`. |
| Volume diverted to storage | Volume diverted to storage | A2 column `VOLUME_DIVERTED_TO_STORAGE`. |
| Volume unit | Volume unit | Column `VOLUME_UNIT`. Allowed values only: `GALLONS`, `ACRE-FEET`. |
| Rediversion status | Rediversion status | Conceptual field. **A1 Data header:** `REDIVERSION_STATUS`. **A2 Data header:** `REDVERSION_STATUS` (Board spelling on Data sheet). Values: `yes` or `no`. |
| DATE | DATE | Column header; format `YYYY-MM-DD`. |
| TIME | TIME | Column header; format `hh:mm:ss` or `hh:mm:ss -n`. |
| Export pack | Export pack | Bundle: Template Data File(s) + methodology draft + filing checklist + audit log. |
| Raw series | Raw series | Immutable ingested readings. |
| Derived series | Derived series | Values after methods / QA / apportionment. |
| Do not certify | Do not certify | Banner/copy rule: never claim the software certified compliance or QI attestation. |

| Landing page | Landing page | Public or shareable intro page for the product prototype. |
| What-if demo | What-if demo | Interactive sample scenario: adjust a few measurements, download demo A1 CSV. Always labeled prototype/demo. |
| Demo A1 CSV | Demo A1 CSV | CSV whose header matches Board A1 Data columns exactly; for demonstration only — not a CalWATRS filing. |
| Prototype | Prototype | Allowed label for early builds; must not claim Board certification or portal submission. |

## Column headers (export; do not rename)

### A1 Data sheet

`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_USE`, `VOLUME_UNIT`, `BENEFICIAL_USE`, `WATER_RIGHT`, `REDIVERSION_STATUS`, `PLACE_OF_USE`

### A2 Data sheet

`DATE`, `TIME`, `FLOW_RATE`, `FLOW_RATE_UNIT`, `VOLUME_DIVERTED_TO_STORAGE`, `VOLUME_UNIT`, `WATER_RIGHT`, `PLACE_OF_STORAGE`, `REDVERSION_STATUS`

## Open questions (wording)

3. Public marketing name for the landing page product — **not decided**; use descriptive phrasing until named.

1. Exact CalWATRS portal labels for methodology form controls — unknown; use §934(a) content headings in the methodology draft until captured.
2. Exact CalWATRS device-type dropdown strings — unknown; free text in v1 registry UI.
