import json
from pathlib import Path

import requests


SEC_JSON_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
HEADERS = {"User-Agent": "MyAppName/1.0 (hi@WhyDRS.org)"}
REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILE = REPO_ROOT / "data" / "SEC-CTEC-Data" / "company_tickers_exchange.json"


def download_and_process_sec_data() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(SEC_JSON_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise SystemExit(f"Failed to download SEC data from {SEC_JSON_URL}: {error}") from error

    json_data = response.json()
    fields = json_data["fields"]
    data = json_data["data"]

    processed_data = []
    for entry in data:
        processed_entry = entry.copy()
        processed_entry[0] = str(processed_entry[0]).strip()
        processed_entry[1] = str(processed_entry[1]).strip()
        processed_entry[2] = str(processed_entry[2]).strip()
        processed_data.append(processed_entry)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump({"fields": fields, "data": processed_data}, file, indent=4)

    print(f"Processed SEC data file saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    download_and_process_sec_data()
