from __future__ import annotations

import os
from typing import List

from flask import Flask, request, abort
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction,
)
from linebot.v3.webhooks import (
    WebhookParser,
    MessageEvent,
    TextMessageContent,
)
from linebot.exceptions import InvalidSignatureError

from .availability import AvailabilityManager

app = Flask(__name__)

config = Configuration(access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", ""))
api_client = ApiClient(config)
line_bot_api = MessagingApi(api_client)
parser = WebhookParser(os.environ.get("LINE_CHANNEL_SECRET", ""))

availability_manager = AvailabilityManager(db_path=os.environ.get("DB_PATH", ":memory:"))


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            handle_text_message(event)
    return "OK"


def handle_text_message(event: MessageEvent) -> None:
    user_id = event.source.user_id
    text = event.message.text.strip().lower()

    if text == "schedule":
        reply_with_timeslots(event.reply_token)
    else:
        timeslots = [slot.strip() for slot in text.split(",") if slot.strip()]
        if timeslots:
            availability_manager.submit_availability(user_id, timeslots)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="Thanks! Availability recorded.")],
                )
            )


def reply_with_timeslots(reply_token: str) -> None:
    buttons = [
        QuickReplyButton(action=MessageAction(label=label, text=label))
        for label in ["Morning", "Afternoon", "Evening"]
    ]
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                TextMessage(
                    text="Select your available times (send multiple comma separated values)",
                    quick_reply=QuickReply(items=buttons),
                )
            ],
        )
    )


def send_nudges(group_members: List[str]) -> None:
    missing = availability_manager.list_missing_users(group_members)
    for user_id in missing:
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text="Hey! Please let us know your availability.")],
            )
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
