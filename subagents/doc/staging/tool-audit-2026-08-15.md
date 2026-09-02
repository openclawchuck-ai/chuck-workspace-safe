# Chuck Doc Tool/Connection Audit - 2026-08-15

## Purpose

Audit documented Chuck Doc tools and connections from `AGENTS.md`, `TOOLS.md`, workspace scripts, and the global security policy. Checks are limited to safe local execution and non-publishing readiness checks.

## Status Key

- OK: Safe check passed or connection/tool is present and usable for the audited purpose.
- BROKEN: Required dependency or execution path failed.
- SKIPPED-SENSITIVE: Check would require credentials, publishing, account changes, or external side effects.
- NEEDS-MAIN: Requires Chuck Main authorization, context, or external state before Doc should proceed.

## Inventory And Results

| Area | Tool / Connection | Method | Status | Evidence | Fix Attempted / Recommended |
|---|---|---|---|---|---|
| Workspace folders | `staging/`, `outputs/`, `diagrams/`, `handoffs/` | Listed folders and permissions. | OK | Required folders exist under the Doc workspace. | No fix needed. |
| Local document rendering | `scripts/render_document.py` | Pending safe render checks for DOCX/XLSX/PPTX. | NEEDS-MAIN | Script exists and imports `python-docx`, `openpyxl`, and `python-pptx`; execution test still pending. | Run minimal render specs and record results below. |
| Mermaid rendering | `scripts/render_mermaid.sh` | Checked script and `mmdc` availability. | BROKEN | Script calls `mmdc`; `command -v mmdc` returned no path. | Install Mermaid CLI or update script to a known available renderer. |
| Graphviz rendering | `scripts/render_graphviz.sh` | Checked script and `dot` availability. | NEEDS-MAIN | Script calls `dot`; `/usr/bin/dot` is available. Execution test still pending. | Run minimal Graphviz render and record result below. |
| SVG conversion / optimization | `scripts/optimize_svg.sh` | Checked script and converter availability. | BROKEN | Script calls `rsvg-convert`; no executable was found in PATH. | Install `librsvg2-bin` / `rsvg-convert`, or rename script if its purpose is conversion rather than optimization. |
| Google publishing wrapper | `scripts/publish_google.sh` | Read wrapper and checked `gog` availability only. | SKIPPED-SENSITIVE | Wrapper invokes `gog docs create`, `gog sheets import`, and `gog slides create-from-markdown`; `gog` binary is present. Publishing was not authorized. | Do not publish during audit. Main can authorize a dry-run-equivalent or test document if needed. |
| Google Docs/Sheets/Slides assumptions | `gog docs`, `gog sheets`, `gog slides` | Pending non-mutating help/readiness check. | NEEDS-MAIN | `TOOLS.md` documents Google Docs, Sheets, and Slides via `gog`; account state not tested yet. | Run `gog --help` / subcommand help only, no create/import. |
| OCR support | `/home/chuck/bin/ocr_pdf.sh` | Checked executable availability only. | OK | `/home/chuck/bin/ocr_pdf.sh` exists in PATH lookup. | No destructive check needed; optional help/read inspection can confirm dependencies. |
| Security policy alignment | Global security policy | Read policy. | OK | Audit avoids secret exposure, publishing, login, account mutation, and treats external content as untrusted. | No fix needed. |

## Safe Render Check Evidence

Pending.

## Notes

- No Google document was created, imported, published, emailed, or shared.
- No secrets or tokens were read or exposed.
