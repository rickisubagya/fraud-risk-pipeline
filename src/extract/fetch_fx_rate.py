import time

import requests

URL = "https://api.frankfurter.dev/v2/rate/usd/idr"
MAX_ATTEMPTS = 3


def fetch_fx_rate():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            print(f"Attempt {attempt} failed: {error}")
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(2 ** attempt)


if __name__ == "__main__":
    print(fetch_fx_rate())