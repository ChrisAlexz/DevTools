# DevTools - AI-Powered Bug Tracking Automation 🤖

An intelligent Slack bot that automatically triages bug reports, creates Jira tickets, and generates GitHub pull requests with AI-suggested fixes.

## 🚀 Features

- **🤖 AI-Powered Analysis**: Uses Google Gemini to understand bug reports and suggest fixes
- **📋 Automatic Jira Tickets**: Creates detailed bug tickets with severity, impact, and reproduction steps
- **🔧 GitHub Integration**: Automatically creates branches and pull requests with proposed fixes
- **💬 Slack Integration**: Responds to mentions in Slack channels with real-time updates
- **🔄 Complete Workflow**: Bug report → Jira ticket → GitHub PR, all automated

## 📸 How It Works

1. **Report a bug** in any Slack channel by mentioning `@DevTools`
2. **AI analyzes** the conversation and generates a fix suggestion
3. **Jira ticket** is automatically created with all details
4. **GitHub branch** is created with the proposed code changes
5. **Pull request** is opened and linked to the Jira ticket
6. **Slack notification** with links to both Jira and GitHub

## 🛠️ Tech Stack

- **Python 3.10+**
- **Google Gemini AI** - For bug analysis and fix generation
- **Slack Bolt** - Slack integration via Socket Mode
- **Jira API** - Issue tracking
- **PyGithub** - GitHub automation
- **Pydantic** - Configuration management
- **Structlog** - Structured logging

## 📋 Prerequisites

- Python 3.10 or higher
- A Slack workspace with admin access
- Jira account (free tier works)
- GitHub account with a repository
- Google Gemini API key (free tier available)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ChrisAlexz/DevTools.git
cd DevTools
```

### 2. Set Up Python Environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

Required environment variables:

| Variable | Description | Where to Find |
|----------|-------------|---------------|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token | Slack App → OAuth & Permissions |
| `SLACK_APP_TOKEN` | App-Level Token | Slack App → Basic Information |
| `SLACK_SIGNING_SECRET` | Signing Secret | Slack App → Basic Information |
| `SLACK_TEAM_ID` | Workspace ID | Slack URL: `/client/T...` |
| `GEMINI_API_KEY` | Google AI API Key | https://ai.google.dev |
| `JIRA_BASE_URL` | Jira Instance URL | e.g., `https://yourname.atlassian.net` |
| `JIRA_EMAIL` | Your Jira Email | Account email |
| `JIRA_API_TOKEN` | Jira API Token | https://id.atlassian.com/manage-profile/security/api-tokens |
| `JIRA_PROJECT_KEY` | Project Key | e.g., `DEV`, `ENG` |
| `GITHUB_APP_ID` | GitHub App ID | GitHub App Settings |
| `GITHUB_INSTALLATION_ID` | Installation ID | After installing GitHub App |
| `GITHUB_PRIVATE_KEY_PATH` | Path to private key | `./certs/your-key.pem` |
| `GITHUB_REPO_FULL_NAME` | Repository | `username/repo-name` |

## 🔑 Setup Guides

### Slack App Setup

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Enable **Socket Mode** and generate an App-Level Token
4. Add **Bot Token Scopes**:
   - `app_mentions:read`
   - `channels:history`
   - `chat:write`
   - `im:history`
   - `im:read`
   - `im:write`
   - `users:read`
5. Install app to workspace
6. Subscribe to **app_mention** event
7. Invite bot to channels: `/invite @DevTools`

### Google Gemini Setup

1. Go to https://ai.google.dev
2. Click **"Get API key"**
3. Create a new API key
4. Copy and add to `.env` file

### Jira Setup

1. Sign up at https://www.atlassian.com/software/jira/free
2. Create a project (Bug tracking template)
3. Generate API token at https://id.atlassian.com/manage-profile/security/api-tokens
4. Note your project key (e.g., `DEV`)

### GitHub App Setup

1. Go to https://github.com/settings/apps
2. Click **"New GitHub App"**
3. Set permissions:
   - **Contents**: Read & Write
   - **Pull Requests**: Read & Write
   - **Metadata**: Read-only
4. Generate and download private key
5. Install app to your repository
6. Save private key to `backend/certs/`

## 🚀 Running the Bot

```bash
cd backend
source .venv/bin/activate
python slack_bot.py
```

You should see:
```
⚡️ Bolt app is running!
```

## 💬 Usage

In any Slack channel where the bot is present:

```
@DevTools There's a bug where the login button doesn't work on mobile devices. 
When users tap it, nothing happens.
```

The bot will:
1. Reply with "⏳ DevTools is analyzing the conversation…"
2. Create a Jira ticket (e.g., `DEV-5`)
3. Create a GitHub branch and PR
4. Reply with links to both

## 📁 Project Structure

```
DevTools/
├── backend/
│   ├── config.py              # Configuration management
│   ├── slack_bot.py           # Slack event handler
│   ├── orchestrator.py        # Main workflow coordinator
│   ├── llm.py                 # Gemini AI integration
│   ├── jira_client.py         # Jira API client
│   ├── github_client.py       # GitHub API client
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   ├── certs/                 # GitHub private keys
│   ├── templates/             # Prompt templates
│   └── utils/                 # Helper functions
├── docs/
│   └── DEPLOYMENT.md          # Production deployment guide
└── README.md
```

## 🔄 Workflow Details

### Bug Report Processing

1. **Slack Mention** → Event captured via Socket Mode
2. **Conversation Parsing** → Full thread context extracted
3. **AI Analysis** → Gemini generates:
   - Bug summary
   - Severity (critical, high, medium, low)
   - Steps to reproduce
   - Impact assessment
   - Suggested code fix
   - Test plan
4. **Jira Ticket Creation** → Structured issue with all details
5. **GitHub Automation**:
   - Creates branch: `devsync/bug-description`
   - Commits suggested fix (if applicable)
   - Opens PR with Jira link
6. **Slack Response** → Links to Jira ticket and PR

## 🎨 Customization

### Change AI Model

Edit `backend/config.py`:
```python
class GeminiSettings(BaseModel):
    api_key: str
    model: str = "gemini-2.0-flash-exp"  # Change model here
```

### Customize Prompts

Edit `backend/llm.py` `_build_prompt()` method to adjust AI behavior.

### Add Default Reviewers

In `.env`:
```bash
DEFAULT_REVIEWERS=username1,username2
```

### Change Code Search Pattern

In `.env`:
```bash
CODE_SEARCH_GLOB=**/*.{js,jsx,py,ts,tsx}
```

## 🐛 Troubleshooting

### Bot not responding in Slack
- Check bot is invited to channel: `/invite @DevTools`
- Verify Socket Mode is enabled
- Check app token has `connections:write` scope

### "Model not found" error
- Verify Gemini API key is correct
- Check model name is valid (use `gemini-2.0-flash-exp`)

### GitHub PR creation fails
- Verify GitHub App has correct permissions
- Check private key path is correct
- Ensure bot has write access to repository

### Jira ticket creation fails
- Verify API token is valid
- Check project key exists
- Ensure issue type "Bug" is available in project

## 📊 Monitoring

Logs are output to stdout using structured logging:

```bash
python slack_bot.py 2>&1 | tee bot.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- Inspired by DevSync!!

## 📧 Contact

Chris - [@ChrisAlexz](https://github.com/ChrisAlexz)

Project Link: [https://github.com/ChrisAlexz/DevTools](https://github.com/ChrisAlexz/DevTools)

---

⭐ If you found this helpful, please star the repository!
