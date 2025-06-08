# LINE Scheduling Bot

This project provides a simple LINE bot in Python that helps coordinate group outings by tracking members' availability and nudging those who haven't responded.

## Features

- **Availability Selection**: Users can send `schedule` to receive quick reply buttons for selecting timeslots. They can submit multiple values separated by commas.
- **Response Tracking**: Availabilities are stored in a SQLite database. The bot can list which members have not replied.
- **Automatic Reminders**: The `send_nudges` function can be called (manually or from a cron job) to push a reminder message to members who haven't responded.

## Running Locally

Install dependencies:

```bash
pip install flask line-bot-sdk pytest
```

The bot uses the v3 API of `line-bot-sdk`. Typical imports look like:

```python
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
```

Export your LINE credentials and run the server:

```bash
export LINE_CHANNEL_SECRET=your_secret
export LINE_CHANNEL_ACCESS_TOKEN=your_token
python -m src.bot
```

The bot exposes a `/callback` endpoint for LINE webhooks.

## Tests

Run tests using `pytest`:

```bash
pytest
```
