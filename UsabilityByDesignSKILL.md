---
name: usability-by-design
description: Use when designing, prompting, reviewing, or shipping any CalWATRS screen, form, list, or message, at phase gates, or when planning onboarding or the training video. Its pre-ship checklist builds usability in rather than patching it later.
---
# Usability by Design

Usability is designed in from the first screen, not patched in after users complain. Every label, message and page layout is written for the person using the app, not for the database. Treat any usability snag as a defect, like a bug: catch it before the screen ships, because a redesign after launch costs far more. This is the Lean Six Sigma idea of building quality in rather than inspecting it out.

## When to apply
- Writing or reviewing any prompt, spec or pull request that adds or changes a screen, form, list, report or message.
- At every phase gate, before a phase counts as done.
- When planning onboarding material or a training video.

## Principles
1. **Speak the user's language.** Use plain-English labels and headings, never raw field or table names (`right_id_number`, `evidence_kind`). Expand acronyms the first time they appear, or give them a tooltip.
2. **Always show context.** Every page and list says whose record it is, such as the client and site, so users never have to guess which record they're looking at.
3. **Separate the views.** Client-level, site-level and device-level information each get a clear view. Pick lists only offer items that fit the current context, so they never mix clients and leave out retired records.
4. **Make the next step obvious.** Each page has one clear primary action. Destructive or irreversible actions are secondary and need confirmation.
5. **Catch mistakes at the field.** Validation messages appear next to the field and say how to fix the problem, not just that it's wrong.
6. **Never lose work.** Use autosave or drafts for long forms, and warn before leaving with unsaved changes.
7. **Keep compliance machinery quiet.** Keep audit trails, revisions and the like working in the background, and surface them only when the user needs them.

## Pre-ship checklist (the core)
Run this before any screen ships. Every "no" is a defect to fix or a deliberate, written exception.
- [ ] **No raw names:** no raw field, table or code names anywhere a user can see them: headings, labels, errors or exports meant for people.
- [ ] **Readable data:** dates and times are in the user's local time zone and labeled. Units are shown. People and records appear by name, not internal ID.
- [ ] **Context on every page:** each page shows which client, site or record it belongs to, and lists include a client or owner column when they span more than one.
- [ ] **Scoped pick lists:** they offer only items for the current client or site, leave out retired or inactive items, and label each choice with enough context to tell items apart.
- [ ] **Clear empty states:** an empty list explains what belongs there and offers the action that adds the first item.
- [ ] **One primary action:** each page has one obvious primary action. Retired or locked records show no edit or delete controls, and the server refuses those actions too.
- [ ] **Detail pages show everything:** a detail page shows everything related to the record, such as a client's sites, devices, evidence and documents, with links. Users shouldn't have to hunt across lists.
- [ ] **Visible files:** uploaded files show their name, size, type and date, and users can open or download them.
- [ ] **Helpful errors:** validation and error messages say what went wrong and how to fix it, in plain words.
- [ ] **Clear confirmations:** confirmation messages say what just happened.
- [ ] **Accessibility basics:** every input has a label, the page works with a keyboard, contrast is readable, and color is never the only signal.
- [ ] **Explainable:** someone could explain the task on this screen in one or two sentences of training narration. If not, simplify the screen.

## Review practice
1. **Walk the tasks:** use realistic dummy data and step through the user walkthrough tasks as a first-time user would.
2. **Log every snag:** record the screen, the task, what happened and the severity. Severity is blocker (can't finish), major (confusing or error-prone) or minor (polish).
3. **Track simple measures:** from phase to phase, track clicks per task, time per task and snag count by severity.
4. **Fix before the gate:** blockers and majors go on the fix list before the phase gate. Minors are batched.
5. **Carry it into build prompts:** include this checklist in every build prompt (for example a Cursor prompt) that touches the user interface, so new screens are built right the first time.
6. **Test with real users when possible:** once one is available, have a real pilot user try the tasks cold. That's the best test.

## Training video (follow-on deliverable)
- **Script early:** script the video from the walkthrough tasks as soon as the screens exist. Any step that's hard to narrate is flagged as a usability defect and goes back through the checklist.
- **Record once:** record only after the screens settle, so the video is made once and stays accurate.
- **Format:** use short chapters, one per everyday task, with dummy data only, plain narration, captions, and an end card.
- **Keep it current:** keep the script beside the walkthrough doc. When a screen changes, update the matching chapter.
- **Rollout:** ship the video with the product rollout as part of onboarding.

## Roles
- **Product analyst bot:** owns the reviews, the snag log and the video script.
- **Coordinator (General Manager):** turns findings into build prompts.
- **Product owner:** approves fixes and the video.

## CalWATRS context
- **Origin:** in the M1 Phase 1 dummy-data load on 2026-10-09, about half of the 14 gaps found were usability problems: raw field names on the list pages, a thin client page that hid rights, diversion points and meters, meter pick lists mixing clients and retired meters, and an audit log showing user IDs and UTC times. They were fixed afterward on `m1-phase1-fixes`, but this checklist exists so new screens are built right the first time.
- **References:** the walkthrough tasks are in `docs/CALWATRS_CLIENT_WALKTHROUGH.md`, and the dummy clients are in `test-data/phase2-dummy/`. The planned client intake is in `docs/PHASE2_CLIENT_INTAKE_SKETCH.md`.
- **Who uses it:** CalWATRS Product Analyst runs the reviews and writes the video script, Valerie (General Manager) turns the findings into Cursor prompts, and Greg approves.
- **What doesn't change:** usability fixes never weaken firm separation, retire-not-delete, revision checks or the audit trail.
