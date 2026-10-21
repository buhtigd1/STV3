#!/usr/bin/env python3

import re
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

SOURCE_URL = "https://raw.githubusercontent.com/sportlive18/Sportlink-wtf/refs/heads/main/Sport.m3u"
OUTPUT_M3U = "stv3.m3u"
OUTPUT_LOG = "stv3.log"

MAX_WORKERS = 50
TIMEOUT = 10


def check_stream(url):
    try:
        r = requests.head(
            url,
            allow_redirects=True,
            timeout=TIMEOUT,
            headers={"User-Agent": "stv3/1.0"},
        )

        if r.status_code < 400:
            return True

        r = requests.get(
            url,
            stream=True,
            timeout=TIMEOUT,
            headers={"User-Agent": "stv3/1.0"},
        )

        return r.status_code < 400

    except Exception:
        return False


def parse_m3u(content):
    entries = []
    lines = content.splitlines()

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            if i + 1 < len(lines):
                entries.append((lines[i], lines[i + 1]))
                i += 2
            else:
                i += 1
        else:
            i += 1

    return entries


def filter_dead_channels(content):
    entries = parse_m3u(content)

    alive = []
    dead = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(check_stream, url): (extinf, url)
            for extinf, url in entries
        }

        for future in as_completed(futures):
            extinf, url = futures[future]

            try:
                if future.result():
                    alive.append((extinf, url))
                else:
                    dead += 1
                    print(f"DEAD: {url}")
            except Exception:
                dead += 1

    result = ["#EXTM3U"]

    for extinf, url in alive:
        result.append(extinf)
        result.append(url)

    return "\n".join(result), len(alive), dead


def download_m3u():
    r = requests.get(
        SOURCE_URL,
        timeout=30,
        headers={"User-Agent": "stv3/1.0"},
    )
    r.raise_for_status()
    return r.text


def write_log(alive, dead, size):
    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        f.write(f"Source: {SOURCE_URL}\n")
        f.write(
            f"Downloaded: {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC\n"
        )
        f.write(f"Alive Channels: {alive}\n")
        f.write(f"Dead Channels: {dead}\n")
        f.write(f"Size: {size} bytes\n")


def main():
    content = download_m3u()

    filtered_content, alive, dead = filter_dead_channels(content)

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write(filtered_content)

    write_log(
        alive=alive,
        dead=dead,
        size=len(filtered_content.encode("utf-8")),
    )

    print(f"Alive: {alive}")
    print(f"Dead: {dead}")
    print(f"Saved: {OUTPUT_M3U}")
    print(f"Saved: {OUTPUT_LOG}")


if __name__ == "__main__":
    main()
