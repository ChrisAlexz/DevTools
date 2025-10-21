from __future__ import annotations

from dataclasses import dataclass

from jira import JIRA

from config import JiraSettings


def _severity_to_priority(severity: str) -> str:
    mapping = {
        "critical": "Highest",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }
    return mapping.get(severity.lower(), "Medium")


@dataclass
class JiraIssue:
    key: str
    url: str


class JiraService:
    def __init__(self, settings: JiraSettings) -> None:
        self.settings = settings
        self.client = JIRA(
            server=settings.base_url,
            basic_auth=(settings.email, settings.api_token),
        )

    def create_issue(self, summary: str, description: str, labels: list[str], severity: str, assignee: str | None) -> JiraIssue:
        fields = {
            "project": {"key": self.settings.project_key},
            "summary": summary[:255],
            "description": description,
            "issuetype": {"name": "Bug"},
            "labels": labels,
            "priority": {"name": _severity_to_priority(severity)},
        }
        if assignee:
            fields["assignee"] = {"name": assignee}

        issue = self.client.create_issue(fields=fields)
        return JiraIssue(key=issue.key, url=f"{self.settings.base_url}/browse/{issue.key}")
