#!/usr/bin/env python3
"""Sync GitHub labels from .github/labels.yml to GitHub repository.

Usage:
    export GITHUB_TOKEN="ghp_..."
    python scripts/sync_labels.py [--dry-run]
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
import yaml

REPO = os.getenv("GITHUB_REPOSITORY", "ARPAHLS/mnemolink")
LABELS_FILE = Path(__file__).parent.parent / ".github" / "labels.yml"


def get_existing_labels(base_url: str, headers: dict) -> dict[str, dict]:
    """Fetch all existing labels from GitHub repository with pagination."""
    existing: dict[str, dict] = {}
    page = 1

    while True:
        url = f"{base_url}?per_page=100&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data:
                    break
                for item in data:
                    existing[item["name"].lower()] = item
                if len(data) < 100:
                    break
                page += 1
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(
                f"[ERROR] Failed to fetch existing labels (HTTP {e.code}): {err_body}",
                file=sys.stderr,
            )
            raise

    return existing


def main():
    dry_run = "--dry-run" in sys.argv

    if not LABELS_FILE.exists():
        print(f"Error: {LABELS_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(LABELS_FILE, "r", encoding="utf-8") as f:
        labels = yaml.safe_load(f) or []

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print(f"Found {len(labels)} labels in {LABELS_FILE}:")
        for lbl in labels:
            print(f"  - {lbl['name']} (#{lbl['color']}): {lbl.get('description', '')}")
        print(
            "\nNote: GITHUB_TOKEN not set. Set GITHUB_TOKEN to sync directly with GitHub API."
        )
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "MnemoLink-Label-Sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    base_url = f"https://api.github.com/repos/{REPO}/labels"
    print(f"Connecting to GitHub API for {REPO}...")

    try:
        existing = get_existing_labels(base_url, headers)
    except Exception:
        sys.exit(1)

    print(f"Retrieved {len(existing)} existing labels from repository.")
    if dry_run:
        print("Dry run mode enabled. No remote modifications will be performed.")

    created_count = 0
    updated_count = 0
    unchanged_count = 0
    error_count = 0

    for lbl in labels:
        name = lbl["name"]
        color = lbl["color"].lstrip("#").lower()
        desc = lbl.get("description", "")
        name_key = name.lower()

        if name_key in existing:
            current = existing[name_key]
            current_color = current.get("color", "").lower()
            current_desc = current.get("description", "") or ""

            # Check if update is required
            if (
                current_color == color
                and current_desc == desc
                and current.get("name") == name
            ):
                print(f"[UNCHANGED] {name} (#{color})")
                unchanged_count += 1
                continue

            if dry_run:
                print(f"[WOULD UPDATE] {name} (#{color})")
                updated_count += 1
                continue

            # Update existing label
            payload = json.dumps(
                {
                    "new_name": name,
                    "color": color,
                    "description": desc,
                }
            ).encode("utf-8")

            url = f"{base_url}/{urllib.parse.quote(current['name'])}"
            req = urllib.request.Request(
                url, data=payload, headers=headers, method="PATCH"
            )

            try:
                with urllib.request.urlopen(req):
                    print(f"[UPDATED] {name} (#{color})")
                    updated_count += 1
                time.sleep(0.3)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                print(
                    f"[ERROR] Failed to update {name} (HTTP {e.code}): {err_body}",
                    file=sys.stderr,
                )
                error_count += 1
        else:
            if dry_run:
                print(f"[WOULD CREATE] {name} (#{color})")
                created_count += 1
                continue

            # Create new label
            payload = json.dumps(
                {
                    "name": name,
                    "color": color,
                    "description": desc,
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                base_url, data=payload, headers=headers, method="POST"
            )

            try:
                with urllib.request.urlopen(req):
                    print(f"[CREATED] {name} (#{color})")
                    created_count += 1
                time.sleep(0.3)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                print(
                    f"[ERROR] Failed to create {name} (HTTP {e.code}): {err_body}",
                    file=sys.stderr,
                )
                error_count += 1

    print("\n" + "=" * 50)
    print(
        f"Label sync summary: {created_count} created, {updated_count} updated, "
        f"{unchanged_count} unchanged, {error_count} errors."
    )
    print("=" * 50)

    if error_count > 0:
        print(f"Sync failed with {error_count} error(s).", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
