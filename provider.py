import requests
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/doms9/iptv/default/M3U8/events.m3u8"

OUTPUT_FILE = "stv3.m3u"
LOG_FILE    = "stv3.log"

HEADER = '#EXTM3U url-tvg=""'

PRIORITY = [
    "[premier league]",
    "[england premier league]",
    "[formula 1]",
    "[f1]",
    "[motogp]",
    "[motorsports]",
    "[football]",
    "[laliga]",
    "[serie a]",
    "[italy serie a]"
]

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        return f"❌ Failed: {url}\n{e}"

def parse_m3u(content):
    lines = content.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            block = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                block.append(next_line)
                if not next_line.startswith("#"):
                    break
                j += 1
            entries.append(block)
            i = j
        else:
            i += 1
    return entries

def clean_extinf(line):
    # Remove unwanted attributes
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-id="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-name="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-logo="[^"]+"', '', line, flags=re.IGNORECASE)
    line = line.replace("|", "").replace(",,", ",")
    return line

def sort_entries(entries):
    def priority_index(block):
        line = block[0].lower()
        for idx, keyword in enumerate(PRIORITY):
            if keyword in line:
                return idx
        return len(PRIORITY)  # non-priority goes last
    return sorted(entries, key=priority_index)

def main():
    log_entries = [f"Run started at {datetime.now().isoformat()}"]

    print("Downloading playlist...")
    source = download(SOURCE_URL)

    print("Parsing playlist...")
    entries = parse_m3u(source)

    before_filter = len(entries)

    # Apply filter: only keep sports-related channels
    entries = [
        block for block in entries
        if any(keyword in block[0].lower() for keyword in PRIORITY)
    ]

    after_filter = len(entries)

    print("Applying ordering...")
    entries = sort_entries(entries)

    print(f"Total channels before filter: {before_filter}")
    print(f"Total channels after filter: {after_filter}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for block in entries:
            for idx, line in enumerate(block):
                if idx == 0:
                    line = clean_extinf(line)
                f.write(line + "\n")

    # Always write a log file
    with open(LOG_FILE, "w", encoding="utf-8") as logf:
        for entry in log_entries:
            logf.write(entry + "\n")
        logf.write(f"Channels before filter: {before_filter}\n")
        logf.write(f"Channels after filter: {after_filter}\n")
        logf.write(f"✅ Done: saved to {OUTPUT_FILE}\n")

    print(f"✅ Done: saved to {OUTPUT_FILE}, log written to {LOG_FILE}")

if __name__ == "__main__":
    main()
