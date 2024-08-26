from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
import time
import os

from dotenv import load_dotenv

# env and utils
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

PREFECT_SERVER_URL = os.getenv("PREFECT_SERVER_URL")

session = requests.Session()


def wait_for_server_ready(max_wait_seconds: int = 150):
    up = False
    deadline = time.time() + max_wait_seconds
    while time.time() <= deadline:
        print(
            f"waiting for prefect server to be ready on {PREFECT_SERVER_URL}/api/health"
        )
        try:
            resp = session.get(
                f"{PREFECT_SERVER_URL}/api/health",
                auth=HTTPBasicAuth(
                    os.environ.get("SUBDOMAIN_USER") or "admin",
                    os.environ.get("SUBDOMAIN_PASSWORD") or "admin",
                ),
            )
            resp.raise_for_status()
            up = resp.json()
            if up is True:
                break
        except Exception:
            pass
        time.sleep(2)
    if not up:
        raise RuntimeError(f"prefect server not ready after {max_wait_seconds} seconds")


def main():
    wait_for_server_ready()


if __name__ == "__main__":
    main()
