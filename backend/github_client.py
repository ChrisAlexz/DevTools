from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from github import Github, GithubIntegration

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
        g = Github(access_token.token)
        repo = g.get_repo(self.settings.repo_full_name)
        return repo, access_token.token

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
        commit_made = False

        # Try to update file if code patch exists
        if analysis.code_patch and analysis.target_file:
            try:
                contents = repo.get_contents(analysis.target_file, ref=branch_name)
                repo.update_file(
                    contents.path,
                    commit_message,
                    analysis.code_patch,
                    contents.sha,
                    branch=branch_name,
                )
                commit_made = True
            except Exception:
                # File doesn't exist, will create placeholder commit below
                pass

        # If no code was committed, create a placeholder README to make the PR valid
        if not commit_made:
            try:
                readme_content = f"""# {jira_key}: {analysis.summary}

## Bug Report
{analysis.impact}

## Steps to Reproduce
{analysis.steps_to_reproduce}

## Suggested Fix
{analysis.code_patch or 'See Jira ticket for details'}
"""
                # Try to update existing JIRA_NOTES.md or create new one
                try:
                    existing = repo.get_contents("JIRA_NOTES.md", ref=branch_name)
                    repo.update_file(
                        "JIRA_NOTES.md",
                        commit_message,
                        readme_content,
                        existing.sha,
                        branch=branch_name,
                    )
                except:
                    # Create new file
                    repo.create_file(
                        f"{jira_key}.md",
                        commit_message,
                        readme_content,
                        branch=branch_name,
                    )
            except Exception as e:
                # Last resort: just don't create PR
                raise Exception(f"Could not create any commits: {e}")

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