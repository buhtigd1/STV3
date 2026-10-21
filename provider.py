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
    Cek apakah URL stream masih hidup.
    """

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True
        )

        ok_codes = (200, 206)

        if r.status_code in ok_codes:
            r.close()
            return True

        r.close()
        return False

    except Exception:
        return False


def filter_playlist(content):
    lines = content.splitlines()

    output = []
    current_block = []

    total_channels = 0
    kept_channels = 0
    removed_channels = 0

    i = 0

    # simpan header
    if lines and lines[0].startswith("#EXTM3U"):
        output.append(lines[0])
        i = 1

    while i < len(lines):

        line = lines[i].strip()

        # komentar biasa / separator
        if not line.startswith("#EXTINF"):
            if (
                line.startswith("===")
                or (
                    line.startswith("#")
                    and not line.startswith("#KODIPROP")
                    and not line.startswith("#EXTVLCOPT")
                )
            ):
                output.append(lines[i])

            i += 1
            continue

        total_channels += 1

        block = []

        # ambil properti sebelum URL
        while i < len(lines):
            block.append(lines[i])

            if i + 1 >= len(lines):
                break

            nxt = lines[i + 1].strip()

            if nxt.startswith("http://") or nxt.startswith("https://"):
                block.append(lines[i + 1])

                stream_url = nxt

                channel_name = "Unknown"
                extinf = lines[i]

                if "," in extinf:
                    channel_name = extinf.split(",", 1)[1].strip()

                print(f"Checking: {channel_name}")

                if check_stream(stream_url):
                    output.extend(block)
                    output.append("")
                    kept_channels += 1
                    print("  OK")
                else:
                    removed_channels += 1
                    print("  REMOVED")

                i += 2
                break

            i += 1

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
        f.write(
            f"Size: {len(content.encode('utf-8'))} bytes\n"
        )


def main():
    try:
        print("Downloading playlist...")
        original = download_m3u()

        print("Checking streams...")
        filtered, total, kept, removed = filter_playlist(original)

        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write(filtered)

        write_log(total, kept, removed, filtered)

        print("\nDone")
        print(f"Total   : {total}")
        print(f"Working : {kept}")
        print(f"Removed : {removed}")
        print(f"Saved   : {OUTPUT_M3U}")
        print(f"Saved   : {OUTPUT_LOG}")

    except Exception as e:
        with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
            f.write(f"ERROR: {e}\n")

        raise


if __name__ == "__main__":
    main()
