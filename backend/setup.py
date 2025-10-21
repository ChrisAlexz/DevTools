"""Utility script to validate configuration before running the bot."""
from __future__ import annotations

from config import settings


def main() -> None:
    print("✅ Environment loaded successfully")
    print("Workspace:", settings.workflow.monorepo_root)
    print("GitHub repo:", settings.github.repo_full_name)
    print("Jira project:", settings.jira.project_key)
    print("Slack team:", settings.slack.team_id)


if __name__ == "__main__":
    main()
