#!/usr/bin/env python3
"""scripts/verify_repo.py: Automated repository health and integrity gate.

Verifies:
1. Zero-Emoji Compliance: Scans Python, YAML, JSON, and Markdown files.
2. Markdown Link Integrity: Verifies relative links in docs/ and root markdown.
3. Catalog Schema Conformance: Validates all personas, memories, lineages, and cards
   against Pydantic schemas.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Ensure mnemolink can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mnemolink import load_persona, load_memory, load_lineage  # noqa: E402
from mnemolink.models import CatalogCard  # noqa: E402

# Unicode emoji range: \U00010000-\U0010ffff, and misc symbols \u2600-\u26ff, \u2700-\u27bf
EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]", flags=re.UNICODE
)

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "0_local_drafts",
    ".agents",
}

CHECK_EXTENSIONS = {".py", ".yaml", ".yml", ".json", ".md"}


def verify_zero_emojis() -> int:
    """Verify that no emojis exist in repository code, manifests, or documentation."""
    print("Checking Zero-Emoji compliance...")
    violations: list[tuple[Path, int, str]] = []

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            path = Path(root) / f
            if path.suffix.lower() in CHECK_EXTENSIONS:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        for line_no, line in enumerate(fh, 1):
                            m = EMOJI_REGEX.search(line)
                            if m:
                                violations.append((path, line_no, line.strip()))
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    if violations:
        print(f"FAILED: Found {len(violations)} emoji violation(s):")
        for path, line_no, snippet in violations[:20]:
            rel_path = path.relative_to(REPO_ROOT)
            print(f"  {rel_path}:{line_no} -> {snippet}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more.")
        return 1

    print("PASSED: Zero emojis found across repository.")
    return 0


def verify_markdown_links() -> int:
    """Verify that all internal relative markdown links resolve to existing files."""
    print("\nChecking Markdown link integrity...")
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    broken_links: list[tuple[Path, str, Path]] = []

    md_files: list[Path] = []
    # Root markdown files
    for f in REPO_ROOT.glob("*.md"):
        md_files.append(f)

    # Docs markdown files
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        for root, dirs, files in os.walk(docs_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for f in files:
                if f.endswith(".md"):
                    md_files.append(Path(root) / f)

    for md_path in md_files:
        try:
            with open(md_path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except Exception as e:
            print(f"Error reading {md_path}: {e}")
            continue

        matches = link_pattern.findall(content)
        for text, url in matches:
            # Ignore external URLs, mailto, anchor-only links
            if url.startswith(("http://", "https://", "mailto:")) or url.startswith(
                "#"
            ):
                continue

            # Strip query string or anchor fragment
            clean_url = url.split("#")[0].split("?")[0].strip()
            if not clean_url:
                continue

            target_path = (md_path.parent / clean_url).resolve()
            if not target_path.exists():
                broken_links.append((md_path, url, target_path))

    if broken_links:
        print(f"FAILED: Found {len(broken_links)} broken relative markdown link(s):")
        for src, url, target in broken_links:
            rel_src = src.relative_to(REPO_ROOT)
            print(f"  {rel_src} -> '{url}' (target does not exist: {target})")
        return 1

    print(f"PASSED: All markdown links resolved cleanly across {len(md_files)} files.")
    return 0


def verify_catalog_schemas() -> int:
    """Validate all catalog personas, memories, lineages, and cards against Pydantic models."""
    print("\nChecking Catalog manifests and cards against Pydantic models...")
    catalog_dir = REPO_ROOT / "mnemolink" / "catalog"
    if not catalog_dir.exists():
        print(f"FAILED: Catalog directory not found at {catalog_dir}")
        return 1

    errors: list[str] = []
    validated_counts = {"personas": 0, "memories": 0, "lineages": 0, "cards": 0}

    # 1. Validate Personas
    personas_dir = catalog_dir / "personas"
    if personas_dir.exists():
        for persona_dir in personas_dir.iterdir():
            if persona_dir.is_dir():
                persona_id = persona_dir.name
                try:
                    p = load_persona(persona_id)
                    assert p.id == persona_id
                    assert len(p.axioms) > 0
                    assert len(p.boundaries) > 0
                    validated_counts["personas"] += 1
                except Exception as e:
                    errors.append(f"Persona '{persona_id}': {e}")

    # 2. Validate Memories
    memories_dir = catalog_dir / "memories"
    if memories_dir.exists():
        for domain_dir in memories_dir.iterdir():
            if domain_dir.is_dir():
                for mem_dir in domain_dir.iterdir():
                    if mem_dir.is_dir():
                        mem_id = f"{domain_dir.name}/{mem_dir.name}"
                        try:
                            m = load_memory(mem_id)
                            assert m.id == mem_id
                            assert 0.0 <= m.salience <= 1.0
                            assert m.memory_type in {
                                "lore",
                                "work",
                                "incident",
                                "relational",
                                "telemetry",
                            }
                            assert len(m.operational_scars) > 0
                            validated_counts["memories"] += 1
                        except Exception as e:
                            errors.append(f"Memory '{mem_id}': {e}")

    # 3. Validate Lineages
    lineages_dir = catalog_dir / "lineages"
    if lineages_dir.exists():
        for lin_dir in lineages_dir.iterdir():
            if lin_dir.is_dir():
                lin_id = lin_dir.name
                try:
                    lin = load_lineage(lin_id)
                    assert lin.id == lin_id
                    assert len(lin.memory_ids) > 0
                    validated_counts["lineages"] += 1
                except Exception as e:
                    errors.append(f"Lineage '{lin_id}': {e}")

    # 4. Validate all card.json files
    for root, _, files in os.walk(catalog_dir):
        if "card.json" in files:
            card_path = Path(root) / "card.json"
            try:
                with open(card_path, "r", encoding="utf-8") as fh:
                    raw_data = json.load(fh)
                card = CatalogCard.model_validate(raw_data)
                assert card.id
                assert card.teleology
                assert card.teleology.primary_goal
                validated_counts["cards"] += 1
            except Exception as e:
                rel = card_path.relative_to(REPO_ROOT)
                errors.append(f"Card '{rel}': {e}")

    if errors:
        print(f"FAILED: Catalog validation encountered {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(
        f"PASSED: Catalog verified cleanly ({validated_counts['personas']} personas, "
        f"{validated_counts['memories']} memories, {validated_counts['lineages']} lineages, "
        f"{validated_counts['cards']} cards)."
    )
    return 0


def main() -> int:
    print("=" * 70)
    print("MnemoLink Automated Repository Integrity & Standards Gate")
    print("=" * 70)

    exit_code = 0
    exit_code |= verify_zero_emojis()
    exit_code |= verify_markdown_links()
    exit_code |= verify_catalog_schemas()

    print("=" * 70)
    if exit_code == 0:
        print("SUCCESS: All repository health and integrity gates PASSED.")
    else:
        print("FAILURE: One or more integrity gates FAILED.")
    print("=" * 70)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
