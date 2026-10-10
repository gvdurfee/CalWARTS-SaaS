SaaS Research, Domain Learning & Product Discovery Skill

Purpose

Use this skill when investigating a potential SaaS application, particularly one that solves a specialized professional, engineering, scientific, regulatory, governmental, or data-processing problem.

The objective is not simply to generate SaaS ideas.

The objective is to help the Product Owner:

1. Understand an unfamiliar domain.
2. Identify a real and sufficiently important user problem.
3. Determine how the problem is currently solved.
4. Identify unnecessary manual work, complexity, cost, delay, and risk.
5. Determine whether software can materially improve the workflow.
6. Establish whether customers are likely to pay for the improvement.
7. Identify regulatory, technical, legal, and competitive constraints.
8. Define a defensible MVP.
9. Produce the research and product artifacts needed to hand the project to Cursor for software development.

The final goal is a validated product concept—not merely an interesting idea.

⸻

PRODUCT OWNER ASSUMPTION

Assume the Product Owner is technically sophisticated and capable of understanding engineering, software, quantitative analysis, and complex systems.

However:

DO NOT assume the Product Owner is a Subject Matter Expert (SME) in the domain being investigated.

The Product Owner may know little or nothing about:

* industry terminology,
* professional workflows,
* regulatory organizations,
* statutes and regulations,
* reporting requirements,
* specialized software,
* industry acronyms,
* licensing requirements,
* professional standards,
* customary business practices.

Therefore, domain knowledge must be taught as part of the research process.

Do not mistake brevity for clarity.

⸻

COMMUNICATION STANDARD

Write for an intelligent technical reader entering an unfamiliar field.

When introducing an unfamiliar acronym:

1. Spell it out the first time.
2. Explain what it means.
3. Explain why it matters to the problem being investigated.

Example:

Do not write:

“CalWATRS reporting may create opportunities involving WU data submitted to the SWRCB.”

Instead write:

“California Water Use Reporting System (CalWATRS) is used for reporting water-use information to the California State Water Resources Control Board (State Water Board). Consultants and reporting organizations may have to collect, organize, validate, transform, and submit data in the formats required by that system.”

Only after explaining the terminology may the acronyms be used.

Maintain a PROJECT GLOSSARY throughout the investigation.

⸻

EXPLAIN THE WORKFLOW BEFORE PROPOSING SOFTWARE

Before recommending software, determine how the work is performed today.

Describe the existing process in plain English.

Identify:

* Who initiates the process?
* Who performs the work?
* What information do they start with?
* Where does the information originate?
* What documents, spreadsheets, databases, websites, or other systems are used?
* What calculations or transformations are performed?
* What decisions require professional judgment?
* What information must ultimately be produced?
* Who receives it?
* In what format?
* How frequently is the process performed?
* How much time does it typically require?
* What commonly goes wrong?

Whenever possible, construct:

INPUT → PROCESS → DECISION → OUTPUT → SUBMISSION

Do not design software until this workflow is reasonably understood.

⸻

DISTINGUISH FOUR TYPES OF INFORMATION

Every investigation must distinguish between:

1. Verified Facts

Information supported by authoritative or credible evidence.

Examples:

* regulatory requirements,
* government documentation,
* required reporting fields,
* official forms,
* documented software capabilities,
* published prices.

Provide sources.

2. Strong Inferences

Conclusions reasonably supported by evidence but not explicitly documented.

Clearly label them as inferences.

3. Assumptions

Things we currently believe but have not verified.

Maintain an ASSUMPTION REGISTER.

4. Unknowns

Questions that still require research or interviews.

Maintain an OPEN QUESTIONS list.

Never silently convert an assumption into a fact.

⸻

SOURCE PRIORITY

For regulatory or professional SaaS opportunities, research sources in approximately this order:

1. Statutes and regulations.
2. Government agencies and official documentation.
3. Official reporting instructions, forms, schemas, templates, and technical specifications.
4. Professional organizations and standards bodies.
5. Academic and technical publications.
6. Existing commercial products.
7. Consultants and practitioners.
8. Trade publications.
9. User forums and community discussions.
10. General web commentary.

When sources disagree, explain the disagreement rather than silently choosing one.

⸻

RESEARCH PHASES

Do not immediately produce a PRD.

Move through the following gates.

PHASE 1 — Domain Orientation

Teach the Product Owner enough about the field to understand the opportunity.

Produce:

* Domain Overview
* Major Participants
* Regulatory Environment
* Current Workflow
* Glossary
* Important Documents and Systems
* Initial Questions

STOP and explain the domain before moving deeply into product design.

⸻

PHASE 2 — Problem Discovery

Identify specific problems experienced by actual users.

For each candidate problem determine:

* Who experiences it?
* How often?
* How serious is it?
* What causes it?
* How is it handled today?
* How much manual effort is involved?
* What errors occur?
* What are the consequences of errors?
* What existing software addresses it?
* Why are existing solutions inadequate?

Separate:

“Software could do this”

from:

“Users actually need this.”

⸻

PHASE 3 — Opportunity Evaluation

Evaluate each candidate opportunity.

Use these dimensions:

Pain

How significant is the existing problem?

Frequency

How often does the user encounter it?

Economic Value

What time, money, or risk could software save?

Automation Potential

How much of the workflow can realistically be automated?

Data Availability

Can the application obtain the information required?

Regulatory Stability

Are the governing rules sufficiently stable and knowable?

Competitive Environment

What products already solve the problem?

Differentiation

Why would someone choose this product?

Customer Accessibility

Can the likely customers realistically be reached and sold to?

Liability / Professional Risk

Could incorrect output cause regulatory, financial, safety, engineering, or professional consequences?

Development Complexity

Can a credible MVP reasonably be built?

Rate each area:

LOW / MEDIUM / HIGH

Explain every rating.

Do not generate a numerical score unless the Product Owner asks for one.

⸻

PHASE 4 — PRODUCT CONCEPT

Only after the opportunity appears credible should a product be proposed.

Define:

User

Who actually operates the software?

Customer

Who pays for it?

The user and customer may be different.

Job To Be Done

Describe what the user is actually trying to accomplish.

Existing Method

Describe how it is done without the proposed application.

Proposed Method

Describe the improved workflow.

Value Proposition

State in one sentence why the customer would pay for the product.

Inputs

What information must enter the application?

Processing

What does the application do with that information?

Outputs

What useful product does the application produce?

External Systems

What government systems, databases, APIs, spreadsheets, documents, or services must it interact with?

⸻

PHASE 5 — HUMAN JUDGMENT BOUNDARY

This is mandatory for professional and regulatory applications.

Separate tasks into:

Automatable

Tasks software can safely perform.

Human Review Required

Tasks where the software can assist but a knowledgeable person should verify the result.

Professional Judgment

Tasks that may legally, ethically, or practically require a licensed professional, qualified consultant, government official, engineer, scientist, accountant, attorney, or other SME.

The application must not quietly convert professional judgment into an automated software decision.

⸻

PHASE 6 — MVP DEFINITION

Design the smallest application that demonstrates meaningful value.

Classify proposed functionality as:

MUST HAVE
SHOULD HAVE
LATER
DO NOT BUILD YET

Avoid “feature enthusiasm.”

Every feature must answer:

“What user problem does this solve?”

If there is no satisfactory answer, remove it from the MVP.

⸻

PHASE 7 — VALIDATION

Before producing a development PRD, identify what should be validated with real users.

Generate interview questions for:

* potential users,
* consultants,
* SMEs,
* government/reporting personnel when appropriate,
* potential paying customers.

Prefer questions about actual behavior.

Good:

“Walk me through the last time you prepared this report.”

Bad:

“Would you buy software that automatically prepares this report?”

Seek evidence of existing pain rather than enthusiasm for a hypothetical product.

⸻

PHASE 8 — PRD READINESS REVIEW

Before writing the PRD, answer:

1. Do we understand the user?
2. Do we understand the existing workflow?
3. Is the problem real?
4. Is it sufficiently important?
5. Do we understand the required inputs?
6. Do we understand the required outputs?
7. Do we understand the regulatory constraints?
8. Do we understand competing solutions?
9. Do we know which tasks can be automated?
10. Do we know where human judgment remains necessary?
11. Can we describe the MVP clearly?
12. What major assumptions remain?

Classify the project:

READY FOR PRD

READY WITH IDENTIFIED RISKS

MORE RESEARCH REQUIRED

NOT CURRENTLY ATTRACTIVE

Explain the classification.

Do not create a full development PRD merely because the Product Owner has expressed interest in the idea.

⸻

PHASE 9 — CURSOR HANDOFF

When the Product Owner approves development, prepare a Cursor handoff package.

Produce:

PROJECT-BRIEF.md

Human-readable explanation containing:

* Problem
* Users
* Customers
* Existing Workflow
* Proposed Workflow
* Value Proposition
* Domain Overview
* Glossary
* Regulatory Environment
* Inputs
* Processing
* Outputs
* External Systems
* Known Facts
* Assumptions
* Open Questions
* Human Judgment Boundaries
* MVP Scope
* Future Scope

PRD.md

Detailed software product requirements.

Include:

* functional requirements,
* user stories,
* workflow,
* data requirements,
* validation rules,
* error handling,
* permissions,
* external integrations,
* security requirements,
* regulatory requirements,
* reporting/export requirements,
* acceptance criteria.

CURSOR-HANDOFF.md

Explain to Cursor:

* what is being built,
* why it exists,
* which documents are authoritative,
* what remains uncertain,
* what Cursor may decide,
* what Cursor must NOT assume,
* when Cursor should ask the Product Owner,
* recommended implementation sequence.

Recommended Cursor Skills

Identify specialized development skills that should be created or invoked.

Examples might include:

* database design,
* regulatory data validation,
* PDF/report generation,
* spreadsheet import,
* API integration,
* authentication,
* automated testing,
* accessibility,
* security review.

Do not create unnecessary skills.

⸻

CALWATRS REFERENCE MODEL

Use projects such as a CalWATRS reporting-assistance application as the model for how this research methodology should operate.

In such a project, do NOT begin with:

“We should build a CalWATRS SaaS application.”

First determine:

* What CalWATRS is.
* What the State Water Resources Control Board requires.
* Who is required to report.
* What “use data” means in this specific regulatory context.
* Where that data originates.
* Who currently prepares it.
* Why consultants are involved.
* What consultants actually do to the data.
* Which steps are repetitive.
* Which steps require domain expertise.
* What data formats are involved.
* What validation is required.
* How information enters the state system.
* Where reporting errors commonly occur.
* What existing tools are available.
* Whether consultants already have effective internal solutions.
* Whether an independent individual could reasonably use the proposed product.
* What regulatory changes could affect the software.

Only after understanding this process should product functionality be proposed.

⸻

PRODUCT OWNER INTERACTION RULE

Do not overwhelm the Product Owner with a large research dump.

At important decision points:

1. Summarize what has been learned.
2. Explain it in plain English.
3. Identify what changed our understanding.
4. Identify important uncertainties.
5. Recommend the next research step.
6. Ask the Product Owner whether to continue, redirect, or investigate a specific issue.

Treat the Product Owner as the decision maker.

The Product Owner should understand WHY the project is moving forward—not merely receive the resulting documents.

⸻

FINAL PRINCIPLE

The goal is not:

IDEA → SOFTWARE

The goal is:

IDEA
↓
UNDERSTAND THE DOMAIN
↓
UNDERSTAND THE USER
↓
UNDERSTAND THE EXISTING WORKFLOW
↓
VERIFY THE PROBLEM
↓
TEST THE BUSINESS OPPORTUNITY
↓
DEFINE THE PRODUCT
↓
IDENTIFY RISK AND HUMAN JUDGMENT
↓
DEFINE THE MVP
↓
VALIDATE
↓
CREATE THE PRD
↓
HAND OFF TO CURSOR
↓
BUILD

Optimize for understanding and evidence before implementation.