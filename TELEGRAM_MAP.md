# TELEGRAM_MAP.md

## Telegram Topic Routing Map

Last Updated: April 2026  
Agent: Chuck (Entrepreneurial Scout 🦀)

This file is the primary routing reference for Telegram forum topics.
Use it whenever posting, reporting, escalating, or sending automated updates.

## Rules

- Do not guess topic IDs.
- Use this file as the source of truth for Telegram topic routing.
- If a task requires posting and no matching topic exists, ask Tony before posting elsewhere.
- If a message is sensitive, prefer `Notifications / Crons` or `System Health & Logs` over casual topics.
- For security-related findings, use `Notifications / Crons` unless the issue is operational or diagnostic, in which case use `System Health & Logs`.
- Always use Chat ID `3843810073` when posting to any topic
- Never ask for the parent chat ID if it exists in this file

## Parent Chat

- Chat ID: -1003843810073
- Type: Telegram Forum Group (Topics Enabled)

All topic thread IDs in this file belong to this parent chat.

When posting to a topic:
- Always use this Chat ID
- Combine with the correct Thread ID from the Topic Map


## Topic Map

| Topic Name | Thread ID | Primary Purpose | Chuck's Directive |
|---|---:|---|---|
| General / Inbox | 2 | Default entry point for new tasks and quick pings | Use for general replies, clarifying questions, and uncategorized requests |
| eBay Assistant | 4 | eBay trends, listing optimization, competitor tracking | Use for eBay-specific research, experiments, and findings |
| Etsy Assistant | 6 | Etsy market pulse, SEO keyword research, shop analysis | Use for Etsy-specific analysis and recommendations |
| Brain Storm | 8 | White-space hunting and new venture ideation | Use for early-stage ideas, opportunity framing, and concept exploration |
| System Health & Logs | 10 | Error reporting, status updates, boot confirmations | Use for failures, degraded systems, debugging updates, and operational health notes |
| Memory & Learning | 12 | Learned concepts and Soul updates | Use for important durable lessons, memory summaries, and reflective updates when explicitly requested |
| Notifications / Crons | 16 | Scheduled output and automated alerts | Use for heartbeats, milestone updates, security alerts, and other proactive notifications |
| Troubleshooting | 55 | Sandbox for fixing broken skills or testing hooks | Use for testing, repair work, experiments, and isolated debugging tasks |
| Dev Playground | 198 | Software development, repo creation, implementation work, test runs | Route to Chuck Dev for project builds and code execution |
| Gov-Ops-Copilot | 696 | Official GovOps project management, SAM.gov opportunity packaging, proposal-support workflow coordination | Route to Chuck Main for project management, coordination, reviews, and handoffs |
| Doc Optimization | 1216 | Coaching Chuck Doc on document quality, presentation style, deck polish, and output direction | Route to Chuck Doc for document coaching, PowerPoint quality improvement, and style-direction work |
| Portfolio Management | 2882 | Portfolio tracking, positioning, holdings research, and management workflows | Route to Chuck Research for market, portfolio, and opportunity research |

## Routing Guidance

### Use General / Inbox when
- a task is new and uncategorized
- Tony is just pinging or starting a conversation
- the correct destination is unclear and the message is low-risk

### Use Brain Storm when
- exploring new product ideas
- comparing opportunity spaces
- shaping rough venture concepts before execution begins

### Use Notifications / Crons when
- sending scheduled updates
- reporting major milestones
- reporting security alerts
- reporting blockers that Tony should see proactively

### Use System Health & Logs when
- reporting tool failures
- reporting broken hooks, skills, or services
- confirming system startup or recovery
- sharing concise operational diagnostics

### Use Troubleshooting when
- testing a new tool, hook, filter, or workflow
- reproducing a bug
- isolating a technical failure without cluttering production topics

## Agent Routing

- General / Inbox → main
- Memory & Learning → main
- Troubleshooting → main
- Brain Storm → research
- Etsy Assistant → research
- eBay Assistant → research
- Notifications / Crons → ops
- System Health & Logs → ops
- Dev Playground → dev
- Gov-Ops-Copilot → main
- Doc Optimization → doc
- Portfolio Management → research
