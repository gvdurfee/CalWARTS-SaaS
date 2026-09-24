# CalWATRS Cursor handoff packet

Docs-only packet for a Cursor coding agent. No application code.

| File | Purpose |
|------|---------|
| `docs/PRD.md` | Product requirements v1 |
| `docs/GLOSSARY.md` | Exact UI / export wording |
| `docs/FIRST_SLICE.md` | Smallest vertical proof path |
| `.cursor/skills/calwatrs-first-slice/SKILL.md` | Skill: read the three docs, build only the first slice, stop for review |
| `calwatrs-sources/template-a1.xlsx` | Board A1 template (Data headers are source of truth) |
| `calwatrs-sources/template-a2.xlsx` | Board A2 template |
| `fixtures/first-slice/` | Sample CSV + expected A1 headers |

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

## How to use in Cursor

1. Copy this folder into the CalWATRS repo root (or open it as the project).
2. In Agent chat, invoke the skill or say: implement `docs/FIRST_SLICE.md` using the calwatrs-first-slice skill.
3. Do not invent stack, login, or out-of-scope features; list missing decisions under Open questions.

CalWATRS product work was paused for HighTowers-Web; this packet is the resume path.
