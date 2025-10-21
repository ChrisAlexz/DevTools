from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackSettings(BaseModel):
    bot_token: str
    app_token: str
    signing_secret: str
    team_id: str


class GeminiSettings(BaseModel):
    api_key: str
    model: str = "gemini-2.0-flash-exp"


class JiraSettings(BaseModel):
    base_url: str
    email: str
    api_token: str
    project_key: str


class GitHubSettings(BaseModel):
    app_id: str
    installation_id: str
    private_key_path: Path
    repo_full_name: str
    main_branch: str = "main"


class WorkflowSettings(BaseModel):
    monorepo_root: Path = Path(".")
    code_search_glob: str = "src/**/*.py"
    default_assignee: Optional[str] = None
    default_reviewers: List[str] = []


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Slack
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str
    SLACK_SIGNING_SECRET: str
    SLACK_TEAM_ID: str

    # Gemini
    GEMINI_API_KEY: str

    # Jira
    JIRA_BASE_URL: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_PROJECT_KEY: str

    # GitHub
    GITHUB_APP_ID: str
    GITHUB_INSTALLATION_ID: str
    GITHUB_PRIVATE_KEY_PATH: str
    GITHUB_REPO_FULL_NAME: str
    GITHUB_MAIN_BRANCH: str = "main"

    # Workflow
    MONOREPO_ROOT: str = "."
    CODE_SEARCH_GLOB: str = "src/**/*.py"
    DEFAULT_ASSIGNEE: Optional[str] = None
    DEFAULT_REVIEWERS: Optional[str] = None

    @property
    def slack(self) -> SlackSettings:
        return SlackSettings(
            bot_token=self.SLACK_BOT_TOKEN,
            app_token=self.SLACK_APP_TOKEN,
            signing_secret=self.SLACK_SIGNING_SECRET,
            team_id=self.SLACK_TEAM_ID,
        )

    @property
    def gemini(self) -> GeminiSettings:
        return GeminiSettings(api_key=self.GEMINI_API_KEY)

    @property
    def jira(self) -> JiraSettings:
        return JiraSettings(
            base_url=self.JIRA_BASE_URL,
            email=self.JIRA_EMAIL,
            api_token=self.JIRA_API_TOKEN,
            project_key=self.JIRA_PROJECT_KEY,
        )

    @property
    def github(self) -> GitHubSettings:
        return GitHubSettings(
            app_id=self.GITHUB_APP_ID,
            installation_id=self.GITHUB_INSTALLATION_ID,
            private_key_path=Path(self.GITHUB_PRIVATE_KEY_PATH),
            repo_full_name=self.GITHUB_REPO_FULL_NAME,
            main_branch=self.GITHUB_MAIN_BRANCH,
        )

    @property
    def workflow(self) -> WorkflowSettings:
        reviewers = []
        if self.DEFAULT_REVIEWERS:
            reviewers = [r.strip() for r in self.DEFAULT_REVIEWERS.split(",") if r.strip()]
        
        return WorkflowSettings(
            monorepo_root=Path(self.MONOREPO_ROOT),
            code_search_glob=self.CODE_SEARCH_GLOB,
            default_assignee=self.DEFAULT_ASSIGNEE,
            default_reviewers=reviewers,
        )


settings = Settings()