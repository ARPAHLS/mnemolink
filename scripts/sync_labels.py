#!/usr/bin/env python3
"""
Sync GitHub labels from .github/labels.yml to GitHub repository.
Usage:
    export GITHUB_TOKEN="ghp_..."
    python scripts/sync_labels.py
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
import yaml

REPO = os.getenv("GITHUB_REPOSITORY", "ARPAHLS/mnemolink")
LABELS_FILE = Path(__file__).parent.parent / ".github" / "labels.yml"


def main():
    if not LABELS_FILE.exists():
        print(f"Error: {LABELS_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(LABELS_FILE, "r", encoding="utf-8") as f:
        labels = yaml.safe_load(f)

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print(f"Found {len(labels)} labels in {LABELS_FILE}:")
        for lbl in labels:
            print(f"  - {lbl['name']} (#{lbl['color']}): {lbl['description']}")
        print(
            "\nNote: GITHUB_TOKEN not set. Set GITHUB_TOKEN to sync directly with GitHub API."
        )
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "MnemoLink-Label-Sync",
    }

    base_url = f"https://api.github.com/repos/{REPO}/labels"
    print(f"Syncing labels to {REPO}...")

    for lbl in labels:
        name = lbl["name"]
        color = lbl["color"].lstrip("#")
        desc = lbl.get("description", "")

        payload = json.dumps(
            {"name": name, "color": color, "description": desc}
        ).encode("utf-8")

        # Try to update existing label or create new one
        url = f"{base_url}/{urllib.request.quote(name)}"
        req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")

        try:
            with urllib.request.urlopen(req):
                print(f"[UPDATED] {name} (#{color})")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Create label
                create_req = urllib.request.Request(
                    base_url, data=payload, headers=headers, method="POST"
                )
                try:
                    with urllib.request.urlopen(create_req):
                        print(f"[CREATED] {name} (#{color})")
                except urllib.error.HTTPError as create_err:
                    print(
                        f"[ERROR] Failed to create {name}: {create_err.code}",
                        file=sys.stderr,
                    )
            else:
                print(f"[ERROR] Failed to update {name}: {e.code}", file=sys.stderr)

    print("Label sync completed.")


if __name__ == "__main__":
    main()
