from __future__ import annotations

import os
from typing import Any, Dict

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from config import settings
from orchestrator import ConversationContext, DevSyncOrchestrator
from utils.logging_config import configure_logging

configure_logging()

orchestrator = DevSyncOrchestrator()
app = App(token=settings.slack.bot_token, signing_secret=settings.slack.signing_secret)


@app.event("app_mention")
def handle_app_mention(body: Dict[str, Any], say):
    event = body.get("event", {})
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")

    if not channel or not thread_ts:
        return

    try:
        slack_link = app.client.chat_getPermalink(channel=channel, message_ts=thread_ts)["permalink"]
    except SlackApiError:
        slack_link = ""

    history = app.client.conversations_replies(channel=channel, ts=thread_ts)
    messages = [message.get("text", "") for message in history.get("messages", [])]
    raw_text = "\n".join(messages)

    context = ConversationContext(
        channel=channel,
        thread_ts=thread_ts,
        reporter_id=event.get("user", ""),
        slack_permalink=slack_link,
        raw_text=raw_text,
    )

    say(thread_ts=thread_ts, text="⏳ DevSync is analyzing the conversation…")
    result = orchestrator.process_bug_report(context)

    say(
        thread_ts=thread_ts,
        text=(
            f"✅ Created Jira ticket *{result['jira_issue']}* and opened PR: {result['pr_url']}\n"
            "I'll keep this thread updated when tests finish."
        ),
    )


if __name__ == "__main__":
    handler = SocketModeHandler(app, settings.slack.app_token)
    handler.start()
