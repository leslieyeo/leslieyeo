#!/usr/bin/env python3
"""Refresh repository star counts embedded in the profile README files."""

import json
import math
import os
import re
import sys
import urllib.request

OWNER = "leslieyeo"
FILES = ["README.md", "README.zh-CN.md"]
MARKER = re.compile(r"(<!--stars:([\w.\-]+)-->)(.*?)(<!--/stars-->)")
TOKEN = os.environ.get("GITHUB_TOKEN")


def format_count(count: int) -> str:
    if count < 1000:
        return str(count)
    thousands = math.floor(count / 100 + 0.5) / 10
    label = f"{thousands:.1f}".rstrip("0").rstrip(".")
    return f"{label}k"


def fetch_stars(repo: str) -> int:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{repo}",
        headers={"Accept": "application/vnd.github+json"},
    )
    if TOKEN:
        request.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["stargazers_count"]


def main() -> None:
    cache: dict[str, str] = {}
    changed = False

    for path in FILES:
        with open(path, encoding="utf-8") as file:
            source = file.read()

        def replace(match: re.Match[str]) -> str:
            repo = match.group(2)
            if repo not in cache:
                cache[repo] = format_count(fetch_stars(repo))
            return match.group(1) + cache[repo] + match.group(4)

        updated = MARKER.sub(replace, source)
        if updated != source:
            with open(path, "w", encoding="utf-8") as file:
                file.write(updated)
            changed = True

    print("updated" if changed else "no changes")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
