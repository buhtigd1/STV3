import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/doms9/iptv/default/M3U8/events.m3u8"
OUTPUT_FILE = "stv3.m3u"

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"❌ Failed: {url}\n{e}")
        return ""

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

def main():
    print("Downloading playlist...")
    source = download(SOURCE_URL)

    print("Parsing playlist...")
    entries = parse_m3u(source)

    print(f"Total channels found: {len(entries)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for block in entries:
            for idx, line in enumerate(block):
                if idx == 0:
                    line = clean_extinf(line)
                f.write(line + "\n")

    print(f"✅ Done: saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
