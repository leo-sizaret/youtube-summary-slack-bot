from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    VideoUnavailable,
    FetchedTranscript,
)
from youtube_transcript_api.proxies import GenericProxyConfig
from anthropic import Anthropic
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os
import random
import logging

import urllib
import urllib.request
import json

from prompts import prompts


MODEL_NAME = "claude-opus-4-20250514"
MAX_TOKENS = 1024
SEGMENT_INTERVAL = 120  # 2 minutes in seconds

# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# Initialize AI model
model = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])
# Load proxy credentials
PROXY_USERNAME = os.environ["PROXY_USERNAME"]
PROXY_PASSWORD = os.environ["PROXY_PASSWORD"]
PROXY_DOMAIN = os.environ["PROXY_DOMAIN"]
PROXY_PORT = os.environ["PROXY_PORT"]


def extract_youtube_id(url) -> str | None:
    """
    Extracts the YouTube video ID from various forms of YouTube URLs including:
    - Full URLs: https://www.youtube.com/watch?v=...
    - Short URLs: https://youtu.be/...
    - URLs with additional parameters
    - Mobile URLs
    - URLs with 'shorts'
    """
    if not url:
        return None

    # Handle youtu.be URLs
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]

    # Handle all other YouTube URLs
    parsed_url = urlparse(url)

    # Handle youtube.com URLs
    if "youtube.com" in parsed_url.netloc:
        # Get URL parameters
        params = parse_qs(parsed_url.query)

        # Try to get video ID from v parameter
        if "v" in params:
            return params["v"][0]

        # Handle YouTube shorts
        if "/shorts/" in parsed_url.path:
            return parsed_url.path.split("/shorts/")[1]

    return None


def format_for_slack(content) -> str:
    # Replace any potential \n or \t with actual line breaks
    formatted = content.replace("\\n", "\n").replace("\\t", "\t")
    # Add a line break after the title if there isn't one
    if "\n\n" not in formatted[:50]:
        formatted = formatted.replace("\n", "\n\n", 1)
    return formatted


def get_random_pepe_emoji() -> str:
    pepe_emojis = [
        "pepe-happy",
        "pepe_cowboy_fast",
        "9041-pepe-shooting",
        "pepesaber",
        "pepe_dance",
        "pepegalight",
        "pepe-rage",
        "pepe_king",
        "pepe-hihi",
        "pepe-more",
        "pepezoomq",
        "pepe-break",
        "pepe-music",
        "pepe_naruto",
        "pepe-excited",
    ]
    return random.choice(pepe_emojis)


def process_transcript_with_timestamps(transcript: FetchedTranscript) -> str:
    def format_timestamp(seconds):
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    # Create segments with timestamps
    segments = []
    current_text = []
    last_timestamp = 0

    for entry in transcript.snippets:
        current_text.append(entry.text)
        if (
            entry.start - last_timestamp > SEGMENT_INTERVAL
        ):  # New segment every 2 minutes
            segments.append(
                {
                    "text": " ".join(current_text),
                    "timestamp": format_timestamp(last_timestamp),
                }
            )
            current_text = []
            last_timestamp = entry.start

    # Add the last segment
    if current_text:
        segments.append(
            {
                "text": " ".join(current_text),
                "timestamp": format_timestamp(last_timestamp),
            }
        )

    # Create the segments info string
    segments_info = "\n".join(
        [f"[{s['timestamp']}] {s['text'][:100]}..." for s in segments]
    )

    return segments_info


def get_url(elements) -> str:
    if not elements:
        return None

    for el in elements:
        logger.debug(f"Processing element: {el}")
        if el["type"] == "link":
            url_found = el["url"]
            logger.debug(f"URL found: {url_found}")
            return url_found
        elif "elements" in el:
            nested_url = get_url(el.get("elements"))
            if nested_url:  # If we found a URL in the nested elements
                return nested_url
    return None  # Return None if no URL was found in this level


def get_video_title(video_id) -> str:

    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % video_id}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    try:
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            return data["title"]
    except Exception as e:
        print(f"Couldn't get video title, full error: {e}")


def get_video_url_from_slack_event(event) -> str:
    event_blocks = event.get("blocks", [])
    video_url = None
    for block in event_blocks:
        if block["type"] == "rich_text":
            video_url = get_url(block["elements"])
            if video_url:
                break  # Exit the loop once we find a URL

    if video_url:
        logger.info(f"URL found: {video_url}")

    return video_url


def get_transcript(youtube_id: str) -> FetchedTranscript:
    ytt_api = YouTubeTranscriptApi(
        proxy_config=GenericProxyConfig(
            http_url=f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_DOMAIN}:{PROXY_PORT}",
            https_url=f"https://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_DOMAIN}:{PROXY_PORT}",
        )
    )
    return ytt_api.fetch(youtube_id)


def invoke_llm_to_get_summary(transcript: FetchedTranscript):
    segments_info = process_transcript_with_timestamps(transcript)
    full_text = " ".join(entry.text for entry in transcript.snippets)

    message = model.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": f"""
                {prompts[0]}\n\n
                Use these timestamps as reference points: {segments_info}\n\n
                Transcript: {full_text}""",
            }
        ],
    )

    return message

@app.event("app_mention")
def handle_mention(event, say):
    logger.info(f"Received mention event: {event}")  # Debug print

    # Get Slack thread if it exist
    thread_ts = event.get("thread_ts", None)

    # Get user id from Slack
    user_id = event["user"]

    # Extract Youtube URL
    video_url = get_video_url_from_slack_event(event)

    # Look for YouTube URL in the message
    youtube_id = extract_youtube_id(video_url)
    logger.info(f"YouTube ID extracted: {youtube_id}")

    if not youtube_id:
        say("Please provide a valid YouTube URL!")
        logger.warning("No valid YouTube URL provided")
        return

    # Get transcription using Youtube
    try:
        if thread_ts is None:
            progress_msg = say(
                f":{get_random_pepe_emoji()}: summarizing <{video_url}|your video>..."
            )
        else:
            progress_msg = say(
                f":{get_random_pepe_emoji()}: summarizing <{video_url}|your video>...",
                thread_ts=thread_ts,
            )

        # Get transcript
        transcript = get_transcript(youtube_id)

        # Get video title
        title = get_video_title(youtube_id)

        # Process transcript with timestamps, get summary from LLM
        message = invoke_llm_to_get_summary(transcript)

        # Send summary message and save its timestamp
        formatted_summary = format_for_slack(message.content[0].text)

        if thread_ts is None:
            thread_msg = say(
                f"<@{user_id}> :{get_random_pepe_emoji()}: summarized <{video_url}|{title}>, see the thread."
            )
            thread_msg_ts = thread_msg["ts"]
            say(
                f"<{video_url}|{title}> \n {formatted_summary}", thread_ts=thread_msg_ts
            )
        else:
            say(f"<@{user_id}> {formatted_summary}", thread_ts=thread_ts)

        # Delete the progress message
        app.client.chat_delete(channel=event["channel"], ts=progress_msg["ts"])

    # Error handling
    except NoTranscriptFound:
        logger.error(f"Couldn't find English captions for this video.", exc_info=True)
        say(f"Couldn't find English captions for this video.")
    except VideoUnavailable:
        logger.error(
            f"This video is unavailable. It might be private or deleted.", exc_info=True
        )
        say(f"This video is unavailable. It might be private or deleted.")
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        say(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting YouTube Summary Bot...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
