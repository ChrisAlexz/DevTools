from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from github import GithubIntegration

from config import GitHubSettings, WorkflowSettings
from llm import AnalysisResult


def _slugify(summary: str) -> str:
    import re

    words = re.sub(r"[^a-zA-Z0-9\s-]", "", summary).lower().split()
    return "-".join(words[:8]) or "devsync-update"


@dataclass
class PullRequest:
    url: str
    number: int


class GitHubService:
    def __init__(self, settings: GitHubSettings, workflow: WorkflowSettings) -> None:
        self.settings = settings
        self.workflow = workflow
        self.integration = GithubIntegration(settings.app_id, self._load_private_key())

    def _load_private_key(self) -> str:
        with open(self.settings.private_key_path, "r", encoding="utf-8") as fh:
            return fh.read()

    def _get_installation_client(self):
        access_token = self.integration.get_access_token(int(self.settings.installation_id))
        return self.integration.get_github_for_app().get_repo(self.settings.repo_full_name), access_token.token

    def prepare_branch(self, analysis: AnalysisResult) -> str:
        repo, _ = self._get_installation_client()
        base_branch = repo.get_branch(self.settings.main_branch)
        branch_name = f"devsync/{_slugify(analysis.summary)}"

        try:
            repo.get_branch(branch_name)
        except Exception:
            repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
        return branch_name

    def create_pull_request(self, analysis: AnalysisResult, branch_name: str, jira_key: str) -> str:
        repo, token = self._get_installation_client()
        commit_message = f"{jira_key}: {analysis.summary}"

        if analysis.code_patch:
            contents = repo.get_contents(analysis.target_file, ref=branch_name)
            repo.update_file(
                contents.path,
                commit_message,
                analysis.code_patch,
                contents.sha,
                branch=branch_name,
            )

        body = self._build_pr_body(analysis, jira_key)
        pr = repo.create_pull(
            title=f"{jira_key}: {analysis.summary}",
            body=body,
            head=branch_name,
            base=self.settings.main_branch,
        )

        if self.workflow.default_reviewers:
            pr.create_review_request(reviewers=self.workflow.default_reviewers)

        return pr.html_url

    def _build_pr_body(self, analysis: AnalysisResult, jira_key: str) -> str:
        return f"""
## Summary
- Jira: [{jira_key}](https://{jira_key})
- Severity: {analysis.severity}
- Impact: {analysis.impact}

## Proposed Changes
```diff
{analysis.code_patch}
```

## Test Plan
{analysis.test_plan or 'Manual verification required.'}
""".strip()
