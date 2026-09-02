# Doc Tool/Connection Audit - 2026-08-15

## Objective

Audit every Chuck Doc tool and connection documented in `AGENTS.md`, `TOOLS.md`, and workspace scripts.

## Scope

Include:
- `render_document.py`
- Mermaid rendering
- Graphviz rendering
- SVG optimization
- gog publishing/readiness without publishing unless already authorized
- staging/output folders
- OCR support
- Google document tool assumptions

## Source Material

- `/home/chuck/.openclaw/workspace-doc/AGENTS.md`
- `/home/chuck/.openclaw/workspace-doc/TOOLS.md`
- `/home/chuck/.openclaw/workspace-doc/scripts/`
- global security policy at `/home/chuck/repos/chuck-workspace-safe/SECURITY_POLICY.md`

## Deliverable

Create `/home/chuck/.openclaw/workspace-doc/staging/tool-audit-2026-08-15.md`.

## First Artifact Required

Write the staging audit file quickly with:
- inventory table/list
- test command or method
- status: OK / BROKEN / SKIPPED-SENSITIVE / NEEDS-MAIN
- brief evidence
- fix attempted or recommended

## Definition of Done

Done when the staging audit exists and covers Doc's documented tools/connections, with at least minimal local render checks where safe.
