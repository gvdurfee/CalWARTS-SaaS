# CalWATRS Measurement Package

Prototype demo plus the first vertical slice: logger CSV → Totalizer → one A1 Template Data File and an audit log.

| File | Purpose |
|------|---------|
| `docs/PRD.md` | Product requirements v1 |
| `docs/GLOSSARY.md` | Exact UI / export wording |
| `docs/FIRST_SLICE.md` | Smallest vertical proof path |
| `.cursor/skills/calwatrs-first-slice/SKILL.md` | Skill: read the three docs, build only the first slice, stop for review |
| `calwatrs-sources/template-a1.xlsx` | Board A1 template (Data headers are source of truth) |
| `calwatrs-sources/template-a2.xlsx` | Board A2 template |
| `fixtures/first-slice/` | Sample CSV, registry, column map, expected A1 headers |
| `first_slice/` | Local CLI for ingest, Totalizer, A1 export, and the audit log |

## Earliest visible deliverable

Landing page + interactive what-if A1 CSV demo — see Demo slice in `docs/FIRST_SLICE.md`.

### Run the demo

In Cursor’s integrated terminal, from the project folder:

```bash
./open-demo.sh
```

That starts a local server and prints an address like `http://127.0.0.1:8765/`. Cursor opens that address in the Cursor browser. Run it in Cursor’s terminal so the address is detected there.

The same static page is hosted on Vercel. The git remote is a private Cursor Origin repo. Deploy after you are logged in to the Vercel CLI:

```bash
npx vercel --prod --yes
```

```bash
node --test tests/demo-a1-csv.test.mjs
```

The demo is a local static page. Public hosting is still an open question.

## First slice

One sample client, one claimed water right, one measurement device, one CSV, one Totalizer run, one A1 Template Data File, and an append-only audit log. Registry and output are files. A database is not chosen.

From the project folder:

```bash
python3 -m first_slice.ui
```

Open http://127.0.0.1:8766/. Enter the claimed water right once (the sample is `SAMPLE-WR-001`). It stays on every screen. On Ingest, map the logger columns onto the Board A1 fields and check “I confirm this column map” before Run Totalizer. The page then downloads `A1-SAMPLE-WR-001.xlsx`. The same run appends `out/first-slice/audit-log.jsonl` and keeps the raw CSV under `out/first-slice/raw/`.

The workbook is a draft. It does not submit to CalWATRS and it does not certify compliance.

The same engine can run without the page after you have confirmed the fixture map yourself:

```bash
python3 -m first_slice --confirm-map
```

```bash
python3 -m unittest tests/first_slice_test.py
```

## How to use in Cursor

1. Open this folder as the project.
2. The demo slice and the main first slice are already in the repo. Further work (apportionment, A2, methodology, checklist, login) needs an explicit request.
3. Do not invent stack, login, or out-of-scope features; list missing decisions under Open questions.
