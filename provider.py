#!/usr/bin/env python3
# stv3.py

import requests
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/sportlive18/Sportlink-wtf/refs/heads/main/Sport.m3u"

OUTPUT_M3U = "stv3.m3u"
OUTPUT_LOG = "stv3.log"

TIMEOUT = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    )
}


def download_m3u():
    r = requests.get(
        SOURCE_URL,
        headers=HEADERS,
        timeout=30
    )
    r.raise_for_status()
    return r.text


def check_stream(url):
    """
    Validasi apakah URL stream masih hidup.
    Untuk stream DRM, status 403 sering masih valid,
    jadi dianggap online.
    """

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            stream=True,
            allow_redirects=True,
            timeout=TIMEOUT
        )

        status = r.status_code
        r.close()

        return status in (200, 206, 301, 302, 403)

    except Exception:
        return False


def filter_playlist(content):
    lines = content.splitlines()

    output = []

    total_channels = 0
    kept_channels = 0
    removed_channels = 0

    # Pertahankan header EXTM3U apa adanya
    if lines and lines[0].startswith("#EXTM3U"):
        output.append(lines[0])
        output.append("")

    block = []

    for line in lines[1:]:

        line = line.rstrip()

        # Simpan semua metadata channel
        if line.startswith("#"):
            block.append(line)
            continue

        # Ketemu URL stream
        if line.startswith(("http://", "https://")):

            stream_url = line
            total_channels += 1

            channel_name = "Unknown"

            for item in block:
                if item.startswith("#EXTINF:"):

                    if "," in item:
                        channel_name = item.split(",", 1)[1].strip()

                    break

            print(f"Checking: {channel_name}")

            if check_stream(stream_url):

                output.extend(block)
                output.append(stream_url)
                output.append("")

                kept_channels += 1

                print("  OK")

            else:

                removed_channels += 1

                print("  REMOVED")

            block = []

    return (
        "\n".join(output),
        total_channels,
        kept_channels,
        removed_channels
    )


def write_log(total, kept, removed, content):

    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:

        f.write(f"Source: {SOURCE_URL}\n")
        f.write(
            f"Downloaded: "
            f"{datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC\n"
        )
        f.write(f"Total channels: {total}\n")
        f.write(f"Working channels: {kept}\n")
        f.write(f"Removed channels: {removed}\n")
        f.write(f"Lines: {len(content.splitlines())}\n")
        f.write(
            f"Size: {len(content.encode('utf-8'))} bytes\n"
        )


def main():

    try:

        print("Downloading playlist...")
        content = download_m3u()

        print("Checking streams...")
        filtered_content, total, kept, removed = filter_playlist(content)

        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write(filtered_content)

        write_log(
            total,
            kept,
            removed,
            filtered_content
        )

        print("\n===== DONE =====")
        print(f"Total   : {total}")
        print(f"Working : {kept}")
        print(f"Removed : {removed}")
        print(f"Saved   : {OUTPUT_M3U}")
        print(f"Saved   : {OUTPUT_LOG}")

    except Exception as e:

        with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
            f.write(
                f"ERROR: {e}\n"
                f"Time: "
                f"{datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC\n"
            )

        raise


if __name__ == "__main__":
    main()
