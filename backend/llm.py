from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

import google.generativeai as genai

from config import GeminiSettings


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


class GeminiService:
    def __init__(self, settings: GeminiSettings) -> None:
        genai.configure(api_key=settings.api_key)
        self.model = genai.GenerativeModel(settings.model)

    def analyze_conversation(self, text: str, repo_snippets: List[str], slack_link: str) -> AnalysisResult:
        prompt = self._build_prompt(text, repo_snippets, slack_link)
        response = self.model.generate_content(prompt)
        parsed = self._parse_response(response)
        return parsed

    def _build_prompt(self, text: str, repo_snippets: List[str], slack_link: str) -> str:
        snippets_block = "\n\n".join(repo_snippets[:5])
        return (
            "You are DevSync, an expert software triage assistant.\n\n"
            "You will be given a Slack thread describing a bug. "
            "Produce a JSON object with keys: summary, steps_to_reproduce, impact, severity, labels, code_patch, target_file, test_plan.\n\n"
            f"Slack thread permalink: {slack_link}\n\n"
            f"Thread:\n{text}\n\n"
            f"Repository context:\n{snippets_block}\n\n"
            "Respond ONLY with valid JSON, no other text."
        )

    def _parse_response(self, response) -> AnalysisResult:
        content = response.text.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        data = json.loads(content)
        
        return AnalysisResult(
            summary=data.get("summary", ""),
            steps_to_reproduce=data.get("steps_to_reproduce", ""),
            impact=data.get("impact", ""),
            severity=data.get("severity", "Medium"),
            labels=data.get("labels", []),
            code_patch=data.get("code_patch", ""),
            target_file=data.get("target_file", ""),
            test_plan=data.get("test_plan", ""),
        )