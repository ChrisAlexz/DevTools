from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import structlog

from config import settings
from github_client import GitHubService
from jira_client import JiraService
from llm import ClaudeService
from utils.filesystem import load_repo_snippets

logger = structlog.get_logger(__name__)


@dataclass
class ConversationContext:
    channel: str
    thread_ts: str
    reporter_id: str
    slack_permalink: str
    raw_text: str


class DevSyncOrchestrator:
    """Coordinates Slack events, AI reasoning, and external integrations."""

    def __init__(self) -> None:
        self.github = GitHubService(settings.github, settings.workflow)
        self.jira = JiraService(settings.jira)
        self.claude = ClaudeService(settings.anthropic)

    def process_bug_report(self, context: ConversationContext) -> Dict[str, Any]:
        logger.info("processing_bug_report.started", context=context)

        repo_snippets = load_repo_snippets(
            Path(settings.workflow.monorepo_root), settings.workflow.code_search_glob
        )
        logger.info("processing_bug_report.repo_snippets_loaded", snippet_count=len(repo_snippets))

        analysis = self.claude.analyze_conversation(
            text=context.raw_text,
            repo_snippets=repo_snippets,
            slack_link=context.slack_permalink,
        )
        logger.info("processing_bug_report.analysis_finished")

        jira_issue = self.jira.create_issue(
            summary=analysis.summary,
            description=self._format_jira_description(context, analysis),
            labels=analysis.labels,
            severity=analysis.severity,
            assignee=settings.workflow.default_assignee,
        )
        logger.info("processing_bug_report.jira_issue_created", key=jira_issue.key)

        branch_name = self.github.prepare_branch(analysis)
        logger.info("processing_bug_report.branch_ready", branch=branch_name)

        pr_url = self.github.create_pull_request(analysis, branch_name, jira_issue.key)
        logger.info("processing_bug_report.pr_created", pr_url=pr_url)

        return {
            "jira_issue": jira_issue.key,
            "jira_url": jira_issue.url,
            "branch_name": branch_name,
            "pr_url": pr_url,
            "analysis": analysis.model_dump(),
        }

    def _format_jira_description(self, context: ConversationContext, analysis) -> str:
        template = textwrap.dedent(
            f"""
            *Slack Thread:* {context.slack_permalink}
            *Reported by:* <@{context.reporter_id}>

            h2. Summary
            {analysis.summary}

            h2. Steps to Reproduce
            {analysis.steps_to_reproduce or 'See Slack conversation.'}

            h2. Impact
            {analysis.impact}

            h2. Suggested Fix
            {{code}}
            {analysis.code_patch}
            {{code}}
            """
        ).strip()
        return template
