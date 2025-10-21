from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseModel):
    bot_token: str = Field(alias="SLACK_BOT_TOKEN")
    app_token: str = Field(alias="SLACK_APP_TOKEN")
    signing_secret: str = Field(alias="SLACK_SIGNING_SECRET")
    team_id: str = Field(alias="SLACK_TEAM_ID")


class GeminiSettings(BaseModel):
    api_key: str = Field(alias="GEMINI_API_KEY")
    model: str = Field(default="gemini-1.5-pro")


class JiraSettings(BaseModel):
    base_url: str = Field(alias="JIRA_BASE_URL")
    email: str = Field(alias="JIRA_EMAIL")
    api_token: str = Field(alias="JIRA_API_TOKEN")
    project_key: str = Field(alias="JIRA_PROJECT_KEY")


class GitHubSettings(BaseModel):
    app_id: str = Field(alias="GITHUB_APP_ID")
    installation_id: str = Field(alias="GITHUB_INSTALLATION_ID")
    private_key_path: Path = Field(alias="GITHUB_PRIVATE_KEY_PATH")
    repo_full_name: str = Field(alias="GITHUB_REPO_FULL_NAME")
    main_branch: str = Field(alias="GITHUB_MAIN_BRANCH", default="main")


class WorkflowSettings(BaseModel):
    monorepo_root: Path = Field(alias="MONOREPO_ROOT", default=Path("."))
    code_search_glob: str = Field(alias="CODE_SEARCH_GLOB", default="src/**/*.py")
    default_assignee: Optional[str] = Field(alias="DEFAULT_ASSIGNEE", default=None)
    default_reviewers: List[str] = Field(alias="DEFAULT_REVIEWERS", default_factory=list)

    @classmethod
    def validate_default_reviewers(cls, value: Optional[str]) -> List[str]:
        if not value:
            return []
        return [reviewer.strip() for reviewer in value.split(",") if reviewer.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    slack: SlackSettings
    gemini: GeminiSettings
    jira: JiraSettings
    github: GitHubSettings
    workflow: WorkflowSettings

    @classmethod
    def load(cls, env_file: str | Path = ".env") -> "Settings":
        settings = cls(_env_file=env_file)
        workflow_alias_dump = settings.model_dump(by_alias=True).get("workflow", {})
        default_reviewers_value = workflow_alias_dump.get("DEFAULT_REVIEWERS")
        settings.workflow.default_reviewers = WorkflowSettings.validate_default_reviewers(default_reviewers_value)
        return settings


settings = Settings.load()