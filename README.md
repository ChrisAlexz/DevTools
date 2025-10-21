# DevSync Starter Kit

This repository bootstraps a complete workflow that mirrors the "DevSync" demo
outlined in your inspiration brief. It includes:

- A React front-end (this Vite app) that documents the pipeline at a glance.
- A Python backend that wires Slack, Anthropic Claude, Jira, and GitHub together.
- Ready-to-edit prompt templates and deployment documentation.

Use this project as the base for your own automation. The sections below walk you
through cloning, configuring API keys, and running the bot with your own Slack
workspace, Jira project, and GitHub repository.

---

## 1. Clone & Open in VS Code

```bash
# Clone your fork of this repository
git clone https://github.com/YOUR_GITHUB_USERNAME/devsync-starter.git
cd devsync-starter

# (Optional) open the workspace in VS Code
code .
```

> **Tip:** To download only the backend for experimentation, copy the `backend/`
> directory into any Python project and follow the same setup instructions.

---

## 2. Python Environment Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

The backend uses Python 3.10+. Ensure the interpreter selected in VS Code points
at `.venv` after activation (bottom-right corner).

---

## 3. Configure Secrets (`backend/.env`)

Create a `.env` file by copying the template and filling in the placeholders with
your credentials. Every variable is required unless marked optional.

```bash
cp backend/.env.example backend/.env
```

| Variable | Where to find it |
| --- | --- |
| `SLACK_BOT_TOKEN` | Slack App &gt; OAuth &amp; Permissions |
| `SLACK_APP_TOKEN` | Slack App &gt; Basic Information (App-Level Token) |
| `SLACK_SIGNING_SECRET` | Slack App &gt; Basic Information |
| `SLACK_TEAM_ID` | Slack Admin &gt; Workspace Settings |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `JIRA_BASE_URL` | e.g., `https://company.atlassian.net` |
| `JIRA_EMAIL` / `JIRA_API_TOKEN` | Atlassian account + API token |
| `JIRA_PROJECT_KEY` | Jira project key, e.g., `ENG` |
| `GITHUB_APP_ID` | GitHub App settings |
| `GITHUB_INSTALLATION_ID` | GitHub App installation page |
| `GITHUB_PRIVATE_KEY_PATH` | Path to downloaded GitHub App private key |
| `GITHUB_REPO_FULL_NAME` | `org/repo` the bot should patch |
| `GITHUB_MAIN_BRANCH` | Branch to base PRs on (default `main`) |
| `MONOREPO_ROOT` | Root directory to analyze (default `.`) |
| `CODE_SEARCH_GLOB` | Glob for context files (e.g., `src/**/*.py`) |
| `DEFAULT_ASSIGNEE` | (Optional) Jira username to auto-assign |
| `DEFAULT_REVIEWERS` | (Optional) Comma-separated GitHub reviewers |

> **Slack scopes required:** `app_mentions:read`, `channels:history`,
> `chat:write`, `im:history`, `im:read`, `im:write`, `users:read`.

> **GitHub App permissions:** `Contents: Read & Write`, `Pull Requests: Read & Write`,
> `Metadata: Read-only`, plus `Issues: Read & Write` if you also sync comments.

Store the GitHub App private key at the path referenced by
`GITHUB_PRIVATE_KEY_PATH`. The repo ships with `backend/certs/` ignored from git;
create that folder locally to hold the PEM file.

---

## 4. Slack App Checklist

1. Create a new Slack app → From scratch → Select your workspace.
2. Enable **Socket Mode** and generate an **App-Level Token**.
3. Install the app to your workspace to generate the **Bot Token**.
4. Add the scopes listed above.
5. Under **Event Subscriptions**, enable events and subscribe to `app_mention`.
6. Set the Socket Mode app token and bot token in `.env`.
7. Invite the bot user to channels you want monitored.

When you mention `@DevSync` in a thread, the bot replies inside that thread with
status updates and links.

---

## 5. Run the Bot Locally

```bash
cd backend
source .venv/bin/activate
python slack_bot.py
```

You should see `⚡️ Bolt app is running!` in the console. Keep this terminal open
while testing in Slack.

---

## 6. Workflow Overview

1. **Conversation Parsing:** `slack_bot.py` listens for `app_mention` events.
2. **AI Analysis:** `llm.py` sends the conversation + code snippets to Claude 3.5
   Sonnet and expects a JSON response describing the bug and fix.
3. **Jira Ticket:** `jira_client.py` creates a `Bug` issue with severity mapped
   from the AI response.
4. **GitHub Automation:** `github_client.py` creates a branch, applies the patch,
   and opens a pull request with reviewers.
5. **Slack Updates:** The bot replies with ticket + PR URLs.

All business logic lives in `orchestrator.py`. Swap out pieces there if your
organization uses Linear, Azure DevOps, or a different LLM.

---

## 7. Deployment

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for a production-ready checklist
covering secrets management, hosting options, and monitoring.

---

## 8. Customization Ideas

- Extend `backend/templates/` with reusable Anthropic prompt snippets.
- Add automated testing by calling your CI pipeline inside
  `DevSyncOrchestrator.process_bug_report`.
- Swap Claude for OpenAI or Azure OpenAI by updating `llm.py` and the dependency
  list.
- Sync Slack thread replies back to Jira comments for two-way communication.

---

## 9. VS Code Tips

- Use the **Python** and **Slack** extensions to debug events locally.
- Create a `.vscode/launch.json` entry that runs `python backend/slack_bot.py`.
- Format code with `ruff` or `black` (add them to `requirements.txt` if desired).

Happy automating! Mention `@DevSync` in Slack to watch the full flow from bug
report to ready-to-merge pull request.
