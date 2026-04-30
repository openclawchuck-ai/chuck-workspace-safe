# OPERATIONS.md - Chuck Dev

## Working Style

Plan briefly -> build -> verify -> report.

Do not wait silently after starting work. A task counts as active only after a first artifact exists.

## Progress Reporting

Default reporting lane: `Dev Playground` in `TELEGRAM_MAP.md`.

Report when:
- the repo is created
- the first artifact exists
- a test/build completes
- a blocker appears
- Tony needs to inspect something
- you pause, switch tasks, or stop for the session

For sustained active development, send a concise status update roughly every 10-15 minutes even if a milestone is still in progress.

## Good Update Format

- Project
- What changed
- Evidence/path/artifact
- Blocker or next step

Example:
- Project: govcon-proposal-copilot-poc
- What changed: added attachment fetcher and saved first parsed sample
- Evidence: `~/repos/govcon-proposal-copilot-poc/src/fetch_attachments.py`
- Next: run against second sample and validate outputs
