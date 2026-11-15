import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram is not configured; skipping notification")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "text": message},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        logger.warning("Telegram notification failed: %s", type(error).__name__)

def ping_heartbeat(suffix=""):
    url = os.getenv("HEALTHCHECK_URL")
    if not url:
        logger.warning("Heartbeat URL is not configured; skipping heartbeat")
        return
    try:
        requests.get(url + suffix, timeout=10).raise_for_status()
    except requests.RequestException as error:
        logger.warning("Heartbeat ping failed: %s", type(error).__name__)