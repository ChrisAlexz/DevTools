import React from 'react'
import './index.css'

const App = () => {
  return (
    <main className="app">
      <header>
        <h1>DevSync Starter Kit</h1>
        <p>
          Follow the checklist below to configure the Slack bot, API integrations, and
          development workflow described in the repository README.
        </p>
      </header>

      <section>
        <h2>Quick Start</h2>
        <ol>
          <li>Install the Python backend dependencies listed in <code>backend/requirements.txt</code>.</li>
          <li>Create your <code>.env</code> file from <code>backend/.env.example</code> and paste your own API keys.</li>
          <li>Run <code>python setup.py</code> to validate credentials and register slash commands.</li>
          <li>Start the bot with <code>python backend/slack_bot.py</code> and mention <strong>@DevSync</strong> in Slack.</li>
        </ol>
      </section>

      <section>
        <h2>Integrations Overview</h2>
        <ul>
          <li><strong>Slack:</strong> Real-time thread monitoring via Socket Mode.</li>
          <li><strong>Anthropic:</strong> Claude Sonnet 3.5 generates bug summaries and code patches.</li>
          <li><strong>Jira:</strong> Automatic issue creation and linking to Slack threads.</li>
          <li><strong>GitHub:</strong> Branch automation, code analysis, and pull request creation.</li>
        </ul>
      </section>

      <section>
        <h2>Helpful Files</h2>
        <ul>
          <li><code>backend/config.py</code>: Centralized environment loading.</li>
          <li><code>backend/orchestrator.py</code>: Coordinates Slack, AI, Jira, and GitHub work.</li>
          <li><code>backend/templates</code>: Prompt snippets for Anthropic.</li>
          <li><code>docs/DEPLOYMENT.md</code>: Copy/paste deployment checklist.</li>
        </ul>
      </section>
    </main>
  )
}

export default App
