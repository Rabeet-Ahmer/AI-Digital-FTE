# Personal AI Employee (Digital FTE)

An autonomous agentic system designed to handle personal and business tasks. This project implements a **Digital Full-Time Equivalent (FTE)** that monitors input channels, triages work, and executes tasks.

## 🚀 Overview
The Digital FTE is a local-first, agent-driven automation suite. It moves beyond simple chat-based interaction into **proactive agent engineering**, where the AI monitors your environment and manages workloads autonomously.

- **Brain:** [Claude Code](https://claude.com/product/claude-code) acts as the reasoning engine and orchestrator.
- **Memory/GUI:** Obsidian (Markdown) serves as the persistent memory and human-readable management dashboard.
- **Senses:** Background Python "Watchers" monitor sources like Gmail and the local filesystem.
- **Hands:** Model Context Protocol (MCP) servers enable the agent to interact with external systems (Gmail, Browsers, etc.).

## 🏗️ Architecture
The system follows a **Perception → Reasoning → Action** loop:
1. **Perception**: Lightweight scripts (Watchers) monitor inputs and create structured `.md` files in the Obsidian vault.
2. **Reasoning**: Claude Code scans for new work, classifies it by priority, and creates action plans.
3. **Action**: The agent executes moves files, sends emails, or performs system tasks through MCP tools.

## 📂 Project Structure
The implementation is organized within the `Bronze/` directory:

| Path | Purpose |
| :--- | :--- |
| `Bronze/Inbox/` | Drop zone for raw incoming files. |
| `Bronze/Needs_Action/` | Triaged items with YAML frontmatter awaiting processing. |
| `Bronze/Done/` | Archive of completed and processed items. |
| `Bronze/Plans/` | AI-generated action plans for multi-step tasks. |
| `Bronze/Logs/` | Audit logs for all autonomous actions (structured JSON). |
| `Bronze/scripts/` | Standalone Python package containing watcher daemons. |

## 🛠️ Getting Started

### Prerequisites
- **Python 3.13+** (managed via `uv`)
- **Obsidian** (for the dashboard)
- **Claude Code** (the execution engine)

### Deployment
1. **Start the File Watcher:**
   ```bash
   cd Bronze/scripts
   uv sync
   uv run python filesystem_watcher.py
   ```
2. **Start processing work:**
   Invoke Claude Code in the `Bronze/` directory. It will detect tasks in `Needs_Action/` and process them according to the rules in `CLAUDE.md` and `Company_Handbook.md`.

## 🛡️ Security & Operating Principles
- **Local-First**: Metadata, memory, and logic reside in your local filesystem.
- **Human-in-the-Loop**: High-stakes actions (e.g., sending emails, payments) prioritize drafting/approval over direct execution.
- **Hard Rules**: The system explicitly skips sensitive files (`.env`, `.key`, etc.) and logs every action for auditing.


## 📄 License
This project is licensed under the MIT License.
