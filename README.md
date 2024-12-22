# YouTube Summary Slack Bot

A Slack bot that generates insightful summaries of YouTube videos using Claude AI.

## Setup

1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment:
    - Unix/macOS: `source venv/bin/activate`
    - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with:
    - SLACK_BOT_TOKEN=xoxb-your-bot-token
    - SLACK_APP_TOKEN=xapp-your-app-token
    - ANTHROPIC_API_KEY=your-anthropic-key

## Usage
1. Invite the bot to a channel
2. Mention the bot with a YouTube URL: `@youtube-summarizer https://youtube.com/watch?v=...`
3. The bot will:
- Extract the transcript
- Generate a summary with timestamps
- Post the summary and tag the user
