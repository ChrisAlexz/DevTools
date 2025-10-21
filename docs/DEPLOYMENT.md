# Deployment Checklist

Use this list when promoting DevSync to staging/production.

## Infrastructure Options

- **Fly.io / Render / Railway:** Simple to deploy the Socket Mode worker.
- **AWS ECS Fargate:** Schedule the worker with auto-restart and log shipping.
- **Kubernetes:** Package the backend as a container and manage secrets via
  Kubernetes Secrets + External Secrets Operator.

## Required Secrets

Store these securely (1Password, Doppler, AWS Secrets Manager, etc.).

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `SLACK_SIGNING_SECRET`
- `ANTHROPIC_API_KEY`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `GITHUB_APP_ID`
- `GITHUB_INSTALLATION_ID`
- `GITHUB_PRIVATE_KEY` (inline secret, mount to file at runtime)

## Observability

- Forward stdout/stderr to a log aggregator (Datadog, Grafana Loki).
- Add a health-check endpoint by wrapping `slack_bot.py` in a FastAPI shell if you
  need container probes.
- Configure Slack alerting for failed Jira/GitHub calls using the `structlog`
  entries emitted in `orchestrator.py`.

## Testing Before Release

1. Run `python backend/tests/smoke_test.py` (create this file to call the
   orchestrator with fixture data).
2. Trigger a real Slack thread with `@DevSync` in a sandbox channel.
3. Verify a Jira ticket + GitHub branch/PR appear with the correct metadata.
4. Merge the PR and confirm no manual clean-up is required.

## Production Hardening

- Rotate the GitHub App private key and Slack tokens regularly.
- Implement retry logic/backoff around Jira and GitHub calls.
- Cache repository metadata to reduce API calls.
- Guard Claude requests behind rate limiting (Anthropic has RPM limits).
- Add slash commands (`/devsync status`) to expose health and queue length.

## Scaling Tips

- Run multiple worker replicas; Slack Bolt + Socket Mode handle concurrency.
- Persist state (e.g., processed thread IDs) in Redis or DynamoDB to avoid
  duplicate work.
- Add feature flags for code generation vs. ticket-only mode.

Happy shipping!
