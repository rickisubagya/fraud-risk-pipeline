import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _request_with_retries(label, send, attempts=3, timeout=20):
    for attempt in range(1, attempts + 1):
        try:
            send(timeout).raise_for_status()
            return True
        except requests.RequestException as error:
            status = getattr(getattr(error, "response", None), "status_code", None)
            logger.warning(
                "%s attempt %s/%s failed: %s (status %s)",
                label,
                attempt,
                attempts,
                type(error).__name__,
                status,
            )
            if attempt < attempts:
                time.sleep(2 * attempt)
    return False


def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram is not configured; skipping notification")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    return _request_with_retries(
        "Telegram notification",
        lambda timeout: requests.post(
            url, data={"chat_id": chat_id, "text": message}, timeout=timeout
        ),
    )


def ping_heartbeat(suffix=""):
    url = os.getenv("HEALTHCHECK_URL")
    if not url:
        logger.warning("Heartbeat URL is not configured; skipping heartbeat")
        return False

    return _request_with_retries(
        "Heartbeat ping",
        lambda timeout: requests.get(url + suffix, timeout=timeout),
    )