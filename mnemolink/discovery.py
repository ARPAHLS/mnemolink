"""Hierarchical discovery and resolution engine for MnemoLink products.

Implements 3-tier precedence:
  1. Project Local (`./.mnemolink`, `./mnemonics`)
  2. User Store (`~/.mnemolink`, `$MNEMOLINK_PATH`)
  3. Bundled Catalog (shipped inside `mnemolink/catalog`)
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import yaml

from mnemolink.models import CatalogCard, LineageProduct, MemoryProduct, PersonaProduct

MNEMOLINK_PATH_ENV = "MNEMOLINK_PATH"


class DiscoveryTier(str, Enum):
    PROJECT = "project"
    USER = "user"
    BUNDLED = "bundled"
    EXPLICIT = "explicit"


def get_bundled_catalog_root() -> Path:
    """Return the absolute path to the bundled catalog directory."""
    return Path(__file__).resolve().parent / "catalog"


def get_user_catalog_roots() -> List[Path]:
    """Return list of user-configured catalog roots from env or home directory."""
    roots: List[Path] = []
    env_paths = os.environ.get(MNEMOLINK_PATH_ENV, "").strip()
    if env_paths:
        for p in env_paths.split(os.pathsep):
            clean = Path(p.strip()).expanduser().resolve()
            if clean.is_dir():
                roots.append(clean)

    # Standard default ~/.mnemolink
    default_user = Path.home() / ".mnemolink"
    if default_user.is_dir() and default_user not in roots:
        roots.append(default_user)

    return roots


def get_project_catalog_roots(cwd: Optional[Union[str, Path]] = None) -> List[Path]:
    """Return project-local search roots in the current working directory."""
    base = Path(cwd or os.getcwd()).resolve()
    candidates = [
        base / ".mnemolink",
        base / "mnemonics",
        base / "catalog",
    ]
    return [c for c in candidates if c.is_dir()]


class MnemonicResolver:
    """Discovers, indexes, and loads Personas, Memories, and Lineages across tiers."""

    def __init__(self, custom_roots: Optional[List[Path]] = None):
        self.custom_roots = custom_roots or []

    def get_search_hierarchy(self) -> List[Tuple[DiscoveryTier, Path]]:
        """Return ordered list of (tier, path) roots searched in descending precedence."""
        hierarchy: List[Tuple[DiscoveryTier, Path]] = []

        # 0. Custom explicit roots
        for root in self.custom_roots:
            if root.is_dir():
                hierarchy.append((DiscoveryTier.EXPLICIT, root))

        # 1. Project-local roots
        for root in get_project_catalog_roots():
            hierarchy.append((DiscoveryTier.PROJECT, root))

        # 2. User & Environment roots
        for root in get_user_catalog_roots():
            hierarchy.append((DiscoveryTier.USER, root))

        # 3. Bundled catalog root
        bundled = get_bundled_catalog_root()
        if bundled.is_dir():
            hierarchy.append((DiscoveryTier.BUNDLED, bundled))

        return hierarchy

    # --------------------------------------------------------------------------
    # Loader Helpers
    # --------------------------------------------------------------------------

    def _load_yaml(self, path: Path) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _read_text_if_exists(self, path: Path) -> str:
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    # --------------------------------------------------------------------------
    # Persona Loading & Discovery
    # --------------------------------------------------------------------------

    def load_persona_from_dir_or_file(self, target: Path) -> PersonaProduct:
        """Load a PersonaProduct from a bundle directory or standalone YAML file."""
        if target.is_file():
            data = self._load_yaml(target)
            return PersonaProduct(**data)

        # Directory bundle
        manifest_file = None
        for candidate in ["persona.yaml", "manifest.yaml", "persona.yml"]:
            if (target / candidate).is_file():
                manifest_file = target / candidate
                break

        if not manifest_file:
            raise FileNotFoundError(
                f"No persona manifest found in bundle directory {target}"
            )

        data = self._load_yaml(manifest_file)

        # Supplement core philosophy if external philosophy.md exists
        phil_file = target / "philosophy.md"
        if phil_file.is_file() and not data.get("core_philosophy"):
            data["core_philosophy"] = self._read_text_if_exists(phil_file)

        return PersonaProduct(**data)

    def find_persona(self, identifier: str) -> PersonaProduct:
        """Resolve a persona by exact path or registry ID."""
        direct = Path(identifier).expanduser()
        if direct.exists():
            return self.load_persona_from_dir_or_file(direct)

        # Normalize identifier (e.g., 'juris_philosopher' or 'personas/juris_philosopher')
        clean_id = identifier.replace("\\", "/").strip("/")
        if clean_id.startswith("personas/"):
            clean_id = clean_id[len("personas/") :]

        for _, root in self.get_search_hierarchy():
            # Check root/personas/<clean_id>
            candidate_dir = root / "personas" / clean_id
            if candidate_dir.is_dir():
                return self.load_persona_from_dir_or_file(candidate_dir)

            # Check root/<clean_id>
            direct_dir = root / clean_id
            if direct_dir.is_dir() and (
                (direct_dir / "persona.yaml").is_file()
                or (direct_dir / "manifest.yaml").is_file()
            ):
                return self.load_persona_from_dir_or_file(direct_dir)

            # Check root/personas/<clean_id>.yaml
            candidate_file = root / "personas" / f"{clean_id}.yaml"
            if candidate_file.is_file():
                return self.load_persona_from_dir_or_file(candidate_file)

        raise FileNotFoundError(
            f"Persona '{identifier}' could not be resolved across search hierarchy: "
            f"{[str(r) for _, r in self.get_search_hierarchy()]}"
        )

    # --------------------------------------------------------------------------
    # Memory Loading & Discovery
    # --------------------------------------------------------------------------

    def load_memory_from_dir_or_file(self, target: Path) -> MemoryProduct:
        """Load a MemoryProduct from a bundle directory or standalone YAML file."""
        if target.is_file():
            data = self._load_yaml(target)
            return MemoryProduct(**data)

        manifest_file = None
        for candidate in ["memory.yaml", "manifest.yaml", "memory.yml"]:
            if (target / candidate).is_file():
                manifest_file = target / candidate
                break

        if not manifest_file:
            raise FileNotFoundError(
                f"No memory manifest found in bundle directory {target}"
            )

        data = self._load_yaml(manifest_file)

        # Supplement debrief if episode.md exists
        ep_file = target / "episode.md"
        if ep_file.is_file() and not data.get("episode_debrief"):
            data["episode_debrief"] = self._read_text_if_exists(ep_file)

        return MemoryProduct(**data)

    def find_memory(self, identifier: str) -> MemoryProduct:
        """Resolve a memory by exact path or registry ID (e.g. 'legal/clause_ambiguity_scar')."""
        direct = Path(identifier).expanduser()
        if direct.exists():
            return self.load_memory_from_dir_or_file(direct)

        clean_id = identifier.replace("\\", "/").strip("/")
        if clean_id.startswith("memories/"):
            clean_id = clean_id[len("memories/") :]

        for _, root in self.get_search_hierarchy():
            # Check root/memories/<clean_id>
            candidate_dir = root / "memories" / clean_id
            if candidate_dir.is_dir():
                return self.load_memory_from_dir_or_file(candidate_dir)

            # Check root/<clean_id>
            direct_dir = root / clean_id
            if direct_dir.is_dir() and (
                (direct_dir / "memory.yaml").is_file()
                or (direct_dir / "manifest.yaml").is_file()
            ):
                return self.load_memory_from_dir_or_file(direct_dir)

            # Check root/memories/<clean_id>.yaml
            candidate_file = root / "memories" / f"{clean_id}.yaml"
            if candidate_file.is_file():
                return self.load_memory_from_dir_or_file(candidate_file)

        raise FileNotFoundError(
            f"Memory '{identifier}' could not be resolved across search hierarchy: "
            f"{[str(r) for _, r in self.get_search_hierarchy()]}"
        )

    # --------------------------------------------------------------------------
    # Lineage Loading & Discovery
    # --------------------------------------------------------------------------

    def load_lineage_from_dir_or_file(self, target: Path) -> LineageProduct:
        """Load a LineageProduct from a bundle directory or standalone YAML file."""
        if target.is_file():
            data = self._load_yaml(target)
            return LineageProduct(**data)

        manifest_file = None
        for candidate in ["lineage.yaml", "manifest.yaml", "lineage.yml"]:
            if (target / candidate).is_file():
                manifest_file = target / candidate
                break

        if not manifest_file:
            raise FileNotFoundError(
                f"No lineage manifest found in bundle directory {target}"
            )

        data = self._load_yaml(manifest_file)

        narrative_file = target / "narrative.md"
        if narrative_file.is_file() and not data.get("cumulative_narrative"):
            data["cumulative_narrative"] = self._read_text_if_exists(narrative_file)

        return LineageProduct(**data)

    def find_lineage(self, identifier: str) -> LineageProduct:
        """Resolve a lineage by exact path or registry ID."""
        direct = Path(identifier).expanduser()
        if direct.exists():
            return self.load_lineage_from_dir_or_file(direct)

        clean_id = identifier.replace("\\", "/").strip("/")
        if clean_id.startswith("lineages/"):
            clean_id = clean_id[len("lineages/") :]

        for _, root in self.get_search_hierarchy():
            candidate_dir = root / "lineages" / clean_id
            if candidate_dir.is_dir():
                return self.load_lineage_from_dir_or_file(candidate_dir)

            direct_dir = root / clean_id
            if direct_dir.is_dir() and (
                (direct_dir / "lineage.yaml").is_file()
                or (direct_dir / "manifest.yaml").is_file()
            ):
                return self.load_lineage_from_dir_or_file(direct_dir)

            candidate_file = root / "lineages" / f"{clean_id}.yaml"
            if candidate_file.is_file():
                return self.load_lineage_from_dir_or_file(candidate_file)

        raise FileNotFoundError(
            f"Lineage '{identifier}' could not be resolved across search hierarchy: "
            f"{[str(r) for _, r in self.get_search_hierarchy()]}"
        )

    # --------------------------------------------------------------------------
    # Catalog Listing
    # --------------------------------------------------------------------------

    def list_catalog(self, kind: Optional[str] = None) -> List[CatalogCard]:
        """Discover and list all products across the search hierarchy."""
        seen_ids = set()
        cards: List[CatalogCard] = []

        for tier, root in self.get_search_hierarchy():
            # Scan personas
            if kind in (None, "persona", "personas"):
                p_dir = root / "personas"
                if p_dir.is_dir():
                    for entry in p_dir.iterdir():
                        if entry.is_dir() and (
                            (entry / "persona.yaml").is_file()
                            or (entry / "manifest.yaml").is_file()
                        ):
                            try:
                                prod = self.load_persona_from_dir_or_file(entry)
                                if prod.id not in seen_ids:
                                    seen_ids.add(prod.id)
                                    cards.append(
                                        CatalogCard(
                                            id=prod.id,
                                            name=prod.name,
                                            kind="persona",
                                            domain=prod.domain,
                                            summary=prod.summary
                                            or prod.core_philosophy[:120],
                                            version=prod.version,
                                            tags=prod.tags,
                                            tier=tier.value,
                                            path=str(entry),
                                        )
                                    )
                            except Exception:
                                pass

            # Scan memories (supports category subdirectories)
            if kind in (None, "memory", "memories"):
                m_dir = root / "memories"
                if m_dir.is_dir():
                    for cat in m_dir.iterdir():
                        if cat.is_dir():
                            # Could be category dir or direct memory dir
                            has_manifest = (cat / "memory.yaml").is_file() or (
                                cat / "manifest.yaml"
                            ).is_file()
                            targets = (
                                [cat]
                                if has_manifest
                                else [sub for sub in cat.iterdir() if sub.is_dir()]
                            )
                            for mem_entry in targets:
                                try:
                                    mem = self.load_memory_from_dir_or_file(mem_entry)
                                    if mem.id not in seen_ids:
                                        seen_ids.add(mem.id)
                                        cards.append(
                                            CatalogCard(
                                                id=mem.id,
                                                name=mem.name,
                                                kind="memory",
                                                domain=mem.domain,
                                                summary=mem.summary
                                                or mem.episode_debrief[:120],
                                                version=mem.version,
                                                tags=mem.tags,
                                                tier=tier.value,
                                                path=str(mem_entry),
                                            )
                                        )
                                except Exception:
                                    pass

            # Scan lineages
            if kind in (None, "lineage", "lineages"):
                l_dir = root / "lineages"
                if l_dir.is_dir():
                    for entry in l_dir.iterdir():
                        if entry.is_dir() and (
                            (entry / "lineage.yaml").is_file()
                            or (entry / "manifest.yaml").is_file()
                        ):
                            try:
                                lin = self.load_lineage_from_dir_or_file(entry)
                                if lin.id not in seen_ids:
                                    seen_ids.add(lin.id)
                                    cards.append(
                                        CatalogCard(
                                            id=lin.id,
                                            name=lin.name,
                                            kind="lineage",
                                            domain="lineage",
                                            summary=lin.summary
                                            or lin.cumulative_narrative[:120],
                                            version=lin.version,
                                            tags=lin.tags,
                                            tier=tier.value,
                                            path=str(entry),
                                        )
                                    )
                            except Exception:
                                pass

        return cards
