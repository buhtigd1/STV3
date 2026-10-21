#!/usr/bin/env python3
# stv3.py

import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/sportlive18/Sportlink-wtf/refs/heads/main/Sport.m3u"
OUTPUT_M3U = "stv3.m3u"
OUTPUT_LOG = "stv3.log"


def download_m3u():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write(r.text)

    return r.text


def write_log(content):
    lines = len(content.splitlines())

    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        f.write(f"Source: {SOURCE_URL}\n")
        f.write(f"Downloaded: {datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC\n")
        f.write(f"Lines: {lines}\n")
        f.write(f"Size: {len(content.encode('utf-8'))} bytes\n")


def main():
    try:
        content = download_m3u()
        write_log(content)
        print(f"Saved: {OUTPUT_M3U}")
        print(f"Saved: {OUTPUT_LOG}")

    except Exception as e:
        with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
            f.write(f"ERROR: {e}\n")
        raise


if __name__ == "__main__":
    main()
