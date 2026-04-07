# TOOLS.md - Chuck Dev

## Code root
- ~/repos

## GitHub
- Account: openclawchuck-ai
- Repo strategy: one repo per project
- Pushes are allowed for your own project repos

## Trusted wrappers
- /home/chuck/bin/nightly_backup
- /home/chuck/bin/security_report
- /home/chuck/bin/health_report
- /home/chuck/bin/tg_post
- /home/chuck/bin/ingress_scan
- /home/chuck/bin/egress_scan

## Project convention
- Create project repos under ~/repos/<project-name>
- Keep code modular
- Prefer Python for automation tools
- Add README and run instructions

## Google Drive

Tool:
- /home/chuck/bin/gdrive_tool.py

Commands:
- list
- mkdir <name> [parent_id]
- upload <filepath> [parent_id]
- move <file_id> <parent_id]

Use Drive for:
- project deliverables
- exports
- datasets
- shared files between agents
