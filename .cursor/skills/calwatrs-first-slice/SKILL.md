---
name: calwatrs-first-slice
description: >-
  Use when implementing or resuming the CalWATRS Measurement Package first
  vertical slice or the earlier landing-page / what-if A1 demo. Reads
  docs/PRD.md, docs/GLOSSARY.md, and docs/FIRST_SLICE.md; prefers the Demo
  slice (landing + interactive A1 CSV) as the earliest visible deliverable,
  then the main ingest→totalizer→A1+audit path; stops for review. Do not use
  for B/C/D templates, portal submission, auth, or full M1–M8 scope.
---

# CalWATRS first slice

## When this skill applies

The user wants a coding agent to start or continue **only** the first slice of CalWATRS Measurement Package, or points at `docs/FIRST_SLICE.md`.

## Required reading (in order)

1. `docs/PRD.md` — product rules and out-of-scope
2. `docs/GLOSSARY.md` — exact UI and column wording
3. `docs/FIRST_SLICE.md` — slice goal, fixtures, done-when

Do not skip these files. Prefer verified Board A1 Data headers over any older notes that disagree.

## Demo slice priority

If `docs/FIRST_SLICE.md` includes a **Demo slice** (landing page + what-if A1 CSV), implement that **first** (or in parallel only if explicitly asked). It is the earliest visible deliverable for consultant feedback.

Demo rules:
1. Fictional but realistic mid-size ag diversion / A1 scenario.
2. Visitor can adjust a few sample measurements.
3. Download CSV with exact Board A1 Data headers.
4. Plain-language summary of output.
5. Clear prototype/demo labeling — no CalWATRS submit, no compliance certification claim.
6. Record unresolved hosting/sample-data choices under Open questions — do not invent a heavy stack.

After the demo done-when checks pass, stop for review unless the user asks to continue into the main first slice.

## Build rules

1. Implement **only** what `docs/FIRST_SLICE.md` defines for the active track (Demo slice and/or main first slice).
2. Do not invent a login system, cloud multi-tenant stack, or features marked out of scope.
3. If a decision is missing, add it under **Open questions** in the relevant doc or the PR description; do not silently pick a heavy architecture.
4. Use glossary strings for user-visible copy and Board column headers.
5. Retain raw ingest immutably; log transforms.
6. Match A1 **Data** sheet headers exactly when exporting.

## Stop condition

When the active track’s **Done when** / **Demo done when** checks pass (or are blocked only by listed Open questions), **stop for review**. Summarize:

- what was built
- how to run the demo
- tests run
- open questions encountered

Do not continue into apportionment, A2, methodology documents, checklist, or M7 batch work unless the user explicitly expands scope.
