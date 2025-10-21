from __future__ import annotations

from dataclasses import dataclass
from typing import List

import anthropic

from config import AnthropicSettings


@dataclass
class AnalysisResult:
    summary: str
    steps_to_reproduce: str
    impact: str
    severity: str
    labels: List[str]
    code_patch: str
    target_file: str
    test_plan: str

    def model_dump(self) -> dict:
        return {
            "summary": self.summary,
            "steps_to_reproduce": self.steps_to_reproduce,
            "impact": self.impact,
            "severity": self.severity,
            "labels": self.labels,
            "code_patch": self.code_patch,
            "target_file": self.target_file,
            "test_plan": self.test_plan,
        }


class ClaudeService:
    def __init__(self, settings: AnthropicSettings) -> None:
        self.client = anthropic.Anthropic(api_key=settings.api_key)
        self.model = settings.model

    def analyze_conversation(self, text: str, repo_snippets: List[str], slack_link: str) -> AnalysisResult:
        prompt = self._build_prompt(text, repo_snippets, slack_link)
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=0,
            system="You are DevSync, an expert software triage assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        parsed = self._parse_response(response)
        return parsed

    def _build_prompt(self, text: str, repo_snippets: List[str], slack_link: str) -> str:
        snippets_block = "\n\n".join(repo_snippets[:5])
        return (
            "You will be given a Slack thread describing a bug. "
            "Produce a JSON object with keys summary, steps_to_reproduce, impact, severity, labels, code_patch, target_file, test_plan. "
            f"Slack thread permalink: {slack_link}\n\n"
            f"Thread:\n{text}\n\n"
            f"Repository context:\n{snippets_block}"
        )

    def _parse_response(self, response) -> AnalysisResult:
        # Anthropics SDK already returns structured content, but we keep a minimal parser for clarity
        content = response.content[0].text  # type: ignore[attr-defined]
        import json

        data = json.loads(content)
        return AnalysisResult(
            summary=data["summary"],
            steps_to_reproduce=data.get("steps_to_reproduce", ""),
            impact=data.get("impact", ""),
            severity=data.get("severity", "Medium"),
            labels=data.get("labels", []),
            code_patch=data.get("code_patch", ""),
            target_file=data.get("target_file", ""),
            test_plan=data.get("test_plan", ""),
        )
