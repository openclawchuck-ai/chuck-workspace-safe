# eBay Mitchell Audit Document Brief for Chuck Doc

Prepared by: Chuck Main
Date: 2026-04-19

## Objective
Create two polished deliverables for Tony about the eBay Mitchell fishing reel parts audit project:

1. A PowerPoint deck (3 to 5 slides)
2. A Word document outlining the requirements

The materials should present the project as a real operating capability, not a speculative prototype.

## Deliverable 1: PowerPoint
Create a polished PowerPoint with very strong visual quality.

### Audience
Tony, internal strategic review / project alignment.

### Tone
Professional, clear, visually strong, concise, confident.

### Slide goals
Use 3 to 5 slides total.

Recommended structure:
1. Project overview and business problem
2. What the audit already accomplished
3. Current proof/results with real metrics
4. Future product direction: dashboard / risk console
5. Optional final slide: next steps / implementation roadmap

### Visual expectations
- polished layout
- tasteful graphics/icons
- use charts, callouts, and clean tables where helpful
- use imagery relevant to eBay, inventory risk, listings, dashboards, and fishing reel parts if appropriate
- make it feel like a serious internal product concept deck

### Key facts to include
#### Business problem
- Tony has multiple Mitchell fishing reel parts listings on eBay.
- The same part can appear in multiple listings.
- eBay does not reconcile shared inventory across those listings.
- This creates risk of overselling out-of-stock parts.

#### Validated value
- Tony explicitly confirmed the audit found real discrepancies.
- Tony said it likely prevented selling a part that was actually out of stock.
- This means the project has already delivered real operational value.

#### Proof metrics: initial live run
- listings scanned: 2
- total part rows extracted: 111
- overlapping parts: 12
- mismatch rows: 25
- warnings: 37

#### Proof metrics: larger batch run
- listings scanned: 15
- total part rows extracted: 998
- overlapping parts: 61
- mismatch rows: 135
- warnings: 553

#### Important caveat
- Notes in summaries said sample output currently uses mock data plus approved quantity-state rules.
- Also noted that live browser extraction had challenge-gating issues in the current environment.
- Even so, the work produced useful discrepancy detection and validated business value.

#### Future direction
The next phase is to productize the win into a desktop-friendly internal dashboard.
Working name suggestions from Research:
- Mitchell Inventory Risk Console
- eBay Mitchell Audit Dashboard
- Mitchell Parts Audit Console

Core future direction:
- review latest official audit run
- inspect parts needing attention
- identify overlap and mismatch risk
- review by listing and by part
- preserve official run history
- support monthly default cadence with future refresh flexibility

## Deliverable 2: Word Document
Create a clean Word document outlining the requirements.

### Tone
Structured, professional, implementation-friendly.

### Sections to include
1. Executive summary
2. Business problem and validated value
3. Product framing
4. Primary user and use case
5. Requirements
6. Dashboard modules / views
7. Official run model
8. Refresh cadence requirements
9. Future work / next phase

### Requirements to include
Use these core requirements from Research:
- desktop-friendly internal dashboard
- low-friction review from Tony’s computer
- monthly default cadence, but adjustable in future
- official runs clearly separated from test/dev runs
- dashboard should make reviewability, prioritization, reporting, and operational flow easier
- no automatic eBay edits in this phase

### Dashboard modules to include
At minimum, describe:
- Audit Overview screen
- Parts Needing Attention view
- Listing view
- listing detail behavior
- part-level drilldown and discrepancy review

### Key Audit Overview content
- latest official run timestamp
- current configured cadence
- run status
- total listings scanned
- total part rows extracted
- overlapping part count
- mismatch count
- warning count
- high-priority issue count

### Parts Needing Attention view
Include concepts such as:
- part number
- description
- number of listings containing the part
- mismatch flag
- warning flag
- priority level
- affected listings
- filters and sorting by actionable risk

### Listing view
Include:
- listing title
- listing ID
- listing URL
- model family
- extracted part count
- overlap count
- warnings
- last audit timestamp

Listing detail should show:
- all extracted parts in the listing
- quantity states
- which parts overlap across other listings

## Output intent
These are polished deliverables, not raw notes.
The deck should feel presentation-ready.
The Word doc should feel like a real product requirements artifact.

## Source truth
Base the deliverables on:
- validated project value: prevented likely oversell risk
- research next-step framing toward dashboard/productization
- proof metrics from live run and 15-listing batch run

## Current status note for Doc
You are being used as a capability test and formal introduction to the team.
Please produce high-quality deliverables that show strong presentation and documentation craft.
