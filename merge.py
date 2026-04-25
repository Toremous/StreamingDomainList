#!/usr/bin/env python3
"""
Merge streaming domain lists from v2fly/domain-list-community
with a custom local list, outputting plain domains only.
"""

import urllib.request
import re
import sys
import os
from datetime import datetime, timezone

UPSTREAM_SOURCES = {
    "primevideo": "https://github.com/v2fly/domain-list-community/raw/refs/heads/master/data/primevideo",
    "disney":     "https://github.com/v2fly/domain-list-community/raw/refs/heads/master/data/disney",
    "hulu":       "https://github.com/v2fly/domain-list-community/raw/refs/heads/master/data/hulu",
    "hbo":        "https://github.com/v2fly/domain-list-community/raw/refs/heads/master/data/hbo",
    "netflix":    "https://github.com/v2fly/domain-list-community/raw/refs/heads/master/data/netflix",
}

CUSTOM_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lists", "custom.txt")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streaming-domains.txt")

DOMAIN_RE = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)+$')


def is_valid_domain(s):
    return bool(DOMAIN_RE.match(s))


def fetch_url(name, url):
    print(f"  Fetching {name}...", end=" ", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            lines = resp.read().decode("utf-8").splitlines()
        print(f"OK ({len(lines)} lines)")
        return lines
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return []


def parse_upstream(lines):
    entries = set()
    for raw in lines:
        line = raw.strip()
        if "#" in line:
            line = line[:line.index("#")].strip()
        if not line:
            continue
        line = re.split(r'\s+[@&]', line)[0].strip()
        if line.startswith(("keyword:", "regexp:", "include:")):
            continue
        if line.startswith("domain:"):
            line = line[len("domain:"):]
        elif line.startswith("full:"):
            line = line[len("full:"):]
        if is_valid_domain(line):
            entries.add(line.lower())
    return entries


def parse_custom(lines):
    entries = set()
    for raw in lines:
        line = raw.strip()
        if "#" in line:
            line = line[:line.index("#")].strip()
        if not line:
            continue
        if is_valid_domain(line):
            entries.add(line.lower())
        else:
            print(f"  WARNING: skipping invalid entry: {line!r}", file=sys.stderr)
    return entries


def main():
    all_entries = set()

    print("Fetching upstream sources:")
    for name, url in UPSTREAM_SOURCES.items():
        lines = fetch_url(name, url)
        entries = parse_upstream(lines)
        all_entries |= entries
        print(f"    +{len(entries)} valid domains from {name}")

    print("\nLoading custom list...")
    if os.path.exists(CUSTOM_LIST):
        with open(CUSTOM_LIST, encoding="utf-8") as f:
            custom_lines = f.readlines()
        custom_entries = parse_custom(custom_lines)
        new_custom = custom_entries - all_entries
        all_entries |= custom_entries
        print(f"  +{len(custom_entries)} entries ({len(new_custom)} not already in upstream)")
    else:
        print("  custom.txt not found, skipping.")

    sorted_entries = sorted(all_entries)

    header = (
        f"# Streaming domains — merged list\n"
        f"# Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"# Sources: {', '.join(UPSTREAM_SOURCES)} + custom\n"
        f"# Total entries: {len(sorted_entries)}\n"
        f"# Format: plain domains, one per line\n"
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(sorted_entries) + "\n")

    print(f"\nWrote {len(sorted_entries)} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
