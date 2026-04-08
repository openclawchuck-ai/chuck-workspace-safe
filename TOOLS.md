# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

💻 System Layout
Code (Primary Dev Environment)
Root: /home/chuck/repos
Each project = separate repo
Example:
~/repos/chuck-lab
~/repos/product-scorer
📁 Business & Research (Google Drive)
Path: /mnt/g/My Drive/OpenClaw_Exchange/New_Ventures
Used for:
venture briefs
research docs
reports
💬 Communication
Telegram = primary interface
Topics:
Brainstorm → idea generation
Project topics → per-repo work
Notifications/Crons → updates + alerts
🧠 Identity
User: Tony
Agent: Chuck 🦀
Role: Entrepreneurial Scout + Venture Partner
🔐 GitHub
Account: openclawchuck-ai
Auth: SSH
Repo strategy: one repo per project
Default branch: main
Push policy:
ask before pushing
never push directly to main
⚙️ Environment Rules
Code runs in WSL (Linux)
DO NOT use /mnt/c for development
Use /home/chuck/repos only
🧪 Dev Conventions
Always explain how to run scripts
Keep code modular
Prefer Python for quick tools
Use clear file names and structure

### Local Security Model (Ollama)

- Endpoint: http://127.0.0.1:11434
- Model: llama3.1:8b

Use cases:
- input risk classification (prompt injection detection)
- output leak detection (PII, API keys, sensitive data)

Rules:
- Use only for classification and filtering
- Do not replace primary reasoning model
- Prefer fast evaluation over long responses


### Local Security Model (Ollama)

- Endpoint: http://127.0.0.1:11434
- Model: llama3.1:8b

Use cases:
- input risk classification (prompt injection detection)
- output leak detection (PII, API keys, sensitive data)

Rules:
- Use only for classification and filtering
- Do not replace the primary reasoning model
- Prefer fast evaluation over long responses

### Local Security Scripts

- Ingress scanner:
  - `python3 ~/.openclaw/workspace/scripts/ingress_scan.py "<text>"`
- Security scripts are advisory filters used before acting on untrusted content or sending sensitive output

### Telegram Posting

- Parent chat ID: -1003843810073
- Use TELEGRAM_MAP.md for thread IDs

Command:
- tg_post <chat_id> <thread_id> "<message>"

Example:
- tg_post -1003843810073 16 "Security alert test"

Rules:
- Always use TELEGRAM_MAP.md for routing
- Never guess thread IDs
- Use Notifications / Crons for alerts and automated output

### Egress Scanner

- Command:
  - egress_scan "<text>"

Use before:
- sending Telegram messages
- writing files to shared locations
- exposing generated content externally

Purpose:
- detect API keys, PII, sensitive data
- redact or block unsafe output


## Google Drive

Tool:
- /home/chuck/bin/gdrive_tool.py

Purpose:
- shared storage
- file handoff between agents
- persistent document access

Common commands:
- list
- mkdir <name> [parent_id]
- upload <filepath> [parent_id]
- move <file_id> <parent_id>


Verification:
- /home/chuck/bin/gdrive_tool.py list

Token files:
- /home/chuck/.secrets/gdrive-oauth.json
- /home/chuck/.secrets/gdrive-token.json

## YouTube

Local transcript tool:
/home/chuck/bin/youtube_tool.py

This is the authoritative YouTube transcript path.
Do not rely on bundled skills for this workflow.

Add whatever helps you do your job. This is your cheat sheet.
