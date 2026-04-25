#!/usr/bin/env python3
"""
Merge streaming domain lists from v2fly/domain-list-community
with a custom local list, deduplicating the result.
"""

import urllib.request
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

CUSTOM_LIST = os.path.join(os.path.dirname(__file__), "lists", "custom.txt")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "streaming-domains.txt")


def fetch_url(name: str, url: str) -> list[str]:
    print(f"  Fetching {name}...", end=" ", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            lines = resp.read().decode("utf-8").splitlines()
        print(f"OK ({len(lines)} lines)")
        return lines
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return []


def parse_lines(lines: list[str]) -> set[str]:
    """Strip comments and blank lines; return normalised entries."""
    entries = set()
    for raw in lines:
        line = raw.strip()
        # Strip inline comments
        if " #" in line:
            line = line[:line.index(" #")].strip()
        if not line or line.startswith("#"):
            continue
        entries.add(line)
    return entries


def main():
    all_entries: set[str] = set()

    print("Fetching upstream sources:")
    for name, url in UPSTREAM_SOURCES.items():
        lines = fetch_url(name, url)
        entries = parse_lines(lines)
        all_entries |= entries
        print(f"    +{len(entries)} unique entries from {name}")

    print("\nLoading custom list...")
    if os.path.exists(CUSTOM_LIST):
        with open(CUSTOM_LIST, encoding="utf-8") as f:
            custom_lines = f.readlines()
        custom_entries = parse_lines(custom_lines)
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
        f"#\n"
        f"# Format: v2fly domain-list-community\n"
        f"#   domain:<name>   regexp:<pattern>   full:<fqdn>   keyword:<word>\n"
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(sorted_entries) + "\n")

    print(f"\nWrote {len(sorted_entries)} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
