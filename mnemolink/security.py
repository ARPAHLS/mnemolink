"""Static Mnemonic Security Linter & Delimiter Injection Scanner.

Defines the MnemonicLinter engine, security rule suites, AST & text scanners,
and completeness checks for community-submitted and catalog mnemonic products.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from mnemolink.discovery import get_bundled_catalog_root
from mnemolink.models import (
    CatalogCard,
    LineageProduct,
    MemoryProduct,
    PersonaProduct,
)

# Zero-emoji regex matching repo standards
EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]", flags=re.UNICODE
)

# Zero-width spaces, joiners, directional / bidi overrides
ZERO_WIDTH_CHARS = {
    "\u200b": "Zero-width space (U+200B)",
    "\u200c": "Zero-width non-joiner (U+200C)",
    "\u200d": "Zero-width joiner (U+200D)",
    "\ufeff": "Byte order mark / zero-width no-break space (U+FEFF)",
    "\u200e": "Left-to-right mark (U+200E)",
    "\u200f": "Right-to-left mark (U+200F)",
}

BIDI_OVERRIDE_CHARS = {
    "\u202a": "Left-to-Right Embedding (U+202A)",
    "\u202b": "Right-to-Left Embedding (U+202B)",
    "\u202c": "Pop Directional Formatting (U+202C)",
    "\u202d": "Left-to-Right Override (U+202D)",
    "\u202e": "Right-to-Left Override (U+202E)",
    "\u2066": "Left-to-Right Isolate (U+2066)",
    "\u2067": "Right-to-Left Isolate (U+2067)",
    "\u2068": "First Strong Isolate (U+2068)",
    "\u2069": "Pop Directional Isolate (U+2069)",
}

# Delimiter escape patterns designed to escape model context or prompt wrappers
DELIMITER_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    (
        "SEC001_CHATML_DELIMITER",
        re.compile(r"<\|im_(start|end)\|>", re.IGNORECASE),
        "ChatML context delimiter escape sequence detected",
    ),
    (
        "SEC001_LLAMA_INST_DELIMITER",
        re.compile(r"\[/?INST\]|\[/?SYS\]", re.IGNORECASE),
        "Llama/Mistral instruction delimiter escape sequence detected",
    ),
    (
        "SEC001_EOS_BOS_TOKEN",
        re.compile(
            r"<\|endoftext\|>|<s>|</s>|<\|fim_(prefix|middle|suffix)\|>", re.IGNORECASE
        ),
        "Frontier LLM special token escape sequence detected",
    ),
    (
        "SEC001_MNEMOLINK_CONTAINER",
        re.compile(
            r"</?(mnemonic_matrix|personas|memories|lineages|episode_debrief|operational_scars)>",
            re.IGNORECASE,
        ),
        "Unescaped MnemoLink protocol wrapper tag detected",
    ),
    (
        "SEC001_SYSTEM_PROMPT_BOUNDARY",
        re.compile(r"</?system>|</?user>|</?assistant>", re.IGNORECASE),
        "Anthropic/OpenAI role wrapper tag detected in payload",
    ),
    (
        "SEC001_RAW_ROLE_PREFIX",
        re.compile(
            r'(?:^|\n)\s*(?:"""|\'\'\')?\s*(?:system|assistant|admin)\s*:',
            re.IGNORECASE,
        ),
        "Raw system/assistant role injection prefix at line start detected",
    ),
]

# Instruction override heuristics (jailbreak / prompt injection patterns)
INSTRUCTION_OVERRIDE_PATTERNS: List[Tuple[str, re.Pattern, str]] = [
    (
        "SEC002_INSTRUCTION_OVERRIDE",
        re.compile(
            r"\b(?:ignore|disregard|forget|bypass|override)\s+(?:all\s+)?"
            r"(?:previous|prior|above|system|core)\s+"
            r"(?:instructions|prompts|axioms|boundaries|rules|directives)\b",
            re.IGNORECASE,
        ),
        "Adversarial instruction override phrase detected (ignore previous instructions)",
    ),
    (
        "SEC002_DEVELOPER_MODE_JAILBREAK",
        re.compile(
            r"\byou\s+are\s+now\s+(?:in\s+)?"
            r"(?:unconstrained|developer|debug|jailbreak|god|dan)\s+mode\b",
            re.IGNORECASE,
        ),
        "Jailbreak heuristic pattern detected ('you are now in developer/jailbreak mode')",
    ),
    (
        "SEC002_AXIOM_DISREGARD",
        re.compile(
            r"\b(?:disregard\s+axioms|override\s+boundaries|bypass\s+filters|"
            r"disable\s+guardrails)\b",
            re.IGNORECASE,
        ),
        "Axiom and boundary bypass instruction heuristic detected",
    ),
    (
        "SEC002_DO_ANYTHING_NOW",
        re.compile(
            r"\bdo\s+anything\s+now\b",
            re.IGNORECASE,
        ),
        "DAN jailbreak signature detected",
    ),
]

SLUG_PATTERN = re.compile(r"^[a-z0-9_-]+$")
QUALIFIED_ID_PATTERN = re.compile(r"^[a-z0-9_-]+(/[a-z0-9_-]+)?$")


class LintSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    file_path: Path
    rule_id: str
    severity: LintSeverity
    message: str
    line_number: Optional[int] = None
    field_path: Optional[str] = None
    snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": str(self.file_path),
            "line": self.line_number,
            "field": self.field_path,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "snippet": self.snippet,
        }


@dataclass
class LintResult:
    target: str
    scanned_files: int = 0
    scanned_products: int = 0
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == LintSeverity.ERROR]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == LintSeverity.WARNING]

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def is_clean(self, strict: bool = False) -> bool:
        if strict:
            return len(self.issues) == 0
        return self.error_count == 0

    @property
    def passed(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "scanned_files": self.scanned_files,
            "scanned_products": self.scanned_products,
            "passed": self.passed,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [i.to_dict() for i in self.issues],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class MnemonicLinter:
    """Offline deterministic static linter for mnemonic assets.

    Verifies delimiter injection resistance, instruction override heuristics,
    unicode obfuscation, structural completeness, salience bounds, and catalog schemas.
    """

    def __init__(self, strict: bool = False, verbose: bool = False) -> None:
        self.strict = strict
        self.verbose = verbose

    def lint_text(
        self,
        text: str,
        file_path: Optional[Path] = None,
    ) -> List[LintIssue]:
        """Perform static text scanning across raw string content."""
        target_path = file_path or Path("<text>")
        issues: List[LintIssue] = []

        lines = text.splitlines()

        # 1. Zero-Emoji Check
        for line_no, line in enumerate(lines, 1):
            emoji_match = EMOJI_REGEX.search(line)
            if emoji_match:
                issues.append(
                    LintIssue(
                        file_path=target_path,
                        rule_id="SEC004_ZERO_EMOJI",
                        severity=LintSeverity.ERROR,
                        message=f"Emoji character detected: '{emoji_match.group(0)}'",
                        line_number=line_no,
                        snippet=line.strip(),
                    )
                )

        # 2. Unicode Evasion: Zero-width characters & Bidi overrides
        for line_no, line in enumerate(lines, 1):
            for ch in line:
                if ch in ZERO_WIDTH_CHARS:
                    desc = ZERO_WIDTH_CHARS[ch]
                    issues.append(
                        LintIssue(
                            file_path=target_path,
                            rule_id="SEC003_ZERO_WIDTH_SPACE",
                            severity=LintSeverity.ERROR,
                            message=f"Hidden zero-width evasion character detected: {desc}",
                            line_number=line_no,
                            snippet=line.strip(),
                        )
                    )
                elif ch in BIDI_OVERRIDE_CHARS:
                    desc = BIDI_OVERRIDE_CHARS[ch]
                    issues.append(
                        LintIssue(
                            file_path=target_path,
                            rule_id="SEC003_BIDI_OVERRIDE",
                            severity=LintSeverity.ERROR,
                            message=(
                                f"Adversarial bidirectional override character detected: {desc}"
                            ),
                            line_number=line_no,
                            snippet=line.strip(),
                        )
                    )

        # 3. Delimiter Injection Patterns
        for line_no, line in enumerate(lines, 1):
            for rule_id, pattern, desc in DELIMITER_PATTERNS:
                m = pattern.search(line)
                if m:
                    issues.append(
                        LintIssue(
                            file_path=target_path,
                            rule_id=rule_id,
                            severity=LintSeverity.ERROR,
                            message=f"{desc}: '{m.group(0)}'",
                            line_number=line_no,
                            snippet=line.strip(),
                        )
                    )

        # 4. Instruction Override Heuristics
        for line_no, line in enumerate(lines, 1):
            for rule_id, pattern, desc in INSTRUCTION_OVERRIDE_PATTERNS:
                m = pattern.search(line)
                if m:
                    issues.append(
                        LintIssue(
                            file_path=target_path,
                            rule_id=rule_id,
                            severity=LintSeverity.ERROR,
                            message=f"{desc}: '{m.group(0)}'",
                            line_number=line_no,
                            snippet=line.strip(),
                        )
                    )

        return issues

    def lint_file(self, path: Path) -> List[LintIssue]:
        """Lint a single file (YAML manifest, card.json, or text)."""
        issues: List[LintIssue] = []
        if not path.exists():
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="IO001_FILE_NOT_FOUND",
                    severity=LintSeverity.ERROR,
                    message=f"Target file does not exist: {path}",
                )
            )
            return issues

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="SEC003_ENCODING_ERROR",
                        severity=LintSeverity.ERROR,
                        message="File contains invalid UTF-8 byte sequences",
                    )
                )
            except Exception as e:
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="IO002_READ_ERROR",
                        severity=LintSeverity.ERROR,
                        message=f"Could not read file: {e}",
                    )
                )
                return issues

        # Run text scanners
        issues.extend(self.lint_text(content, file_path=path))

        # Run manifest schema & structure checks if YAML or JSON
        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            issues.extend(self._lint_yaml_manifest(path, content))
        elif suffix == ".json" and path.name == "card.json":
            issues.extend(self._lint_card_json(path, content))

        return issues

    def _lint_yaml_manifest(self, path: Path, raw_content: str) -> List[LintIssue]:
        issues: List[LintIssue] = []
        try:
            data = yaml.safe_load(raw_content)
        except yaml.YAMLError as exc:
            line = getattr(getattr(exc, "problem_mark", None), "line", None)
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="SYN001_YAML_SYNTAX",
                    severity=LintSeverity.ERROR,
                    message=f"YAML parsing error: {exc}",
                    line_number=line + 1 if line is not None else None,
                )
            )
            return issues

        if not isinstance(data, dict):
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR000_NOT_A_MAPPING",
                    severity=LintSeverity.ERROR,
                    message="Top-level manifest must be a YAML mapping/dict",
                )
            )
            return issues

        # Determine product type from filename or keys
        fname = path.name.lower()
        if fname in ("persona.yaml", "persona.yml") or "core_philosophy" in data:
            issues.extend(self._lint_persona_dict(path, data))
        elif fname in ("memory.yaml", "memory.yml") or "episode_debrief" in data:
            issues.extend(self._lint_memory_dict(path, data))
        elif fname in ("lineage.yaml", "lineage.yml") or "causal_bridges" in data:
            issues.extend(self._lint_lineage_dict(path, data))
        else:
            # Generic structure check
            issues.extend(self._lint_common_fields(path, data))

        return issues

    def _lint_common_fields(self, path: Path, data: Dict[str, Any]) -> List[LintIssue]:
        issues: List[LintIssue] = []
        prod_id = data.get("id")
        if not prod_id:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR004_MISSING_ID",
                    severity=LintSeverity.ERROR,
                    message="Missing mandatory 'id' identifier",
                    field_path="id",
                )
            )
        elif not QUALIFIED_ID_PATTERN.match(str(prod_id)):
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR004_INVALID_ID_SLUG",
                    severity=LintSeverity.ERROR,
                    message=f"Identifier '{prod_id}' is not a valid alphanumeric slug",
                    field_path="id",
                )
            )

        domain = data.get("domain")
        if domain and not SLUG_PATTERN.match(str(domain)):
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR004_INVALID_DOMAIN_SLUG",
                    severity=LintSeverity.ERROR,
                    message=f"Domain '{domain}' is not a valid alphanumeric slug",
                    field_path="domain",
                )
            )

        name = data.get("name")
        if not name or not str(name).strip():
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR006_MISSING_NAME",
                    severity=LintSeverity.ERROR,
                    message="Missing mandatory 'name' title",
                    field_path="name",
                )
            )

        return issues

    def _lint_persona_dict(self, path: Path, data: Dict[str, Any]) -> List[LintIssue]:
        issues = self._lint_common_fields(path, data)
        try:
            PersonaProduct.model_validate(data)
        except Exception as e:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="SCH001_PERSONA_SCHEMA_ERROR",
                    severity=LintSeverity.ERROR,
                    message=f"Persona schema validation failed: {e}",
                )
            )

        axioms = data.get("axioms", [])
        if not axioms or not isinstance(axioms, list) or len(axioms) == 0:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR007_EMPTY_AXIOMS",
                    severity=LintSeverity.ERROR,
                    message="Persona must contain at least one inviolable axiom",
                    field_path="axioms",
                )
            )

        boundaries = data.get("boundaries", [])
        if not boundaries or not isinstance(boundaries, list) or len(boundaries) == 0:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR008_EMPTY_BOUNDARIES",
                    severity=LintSeverity.ERROR,
                    message="Persona must define at least one operational boundary / refusal",
                    field_path="boundaries",
                )
            )

        return issues

    def _lint_memory_dict(self, path: Path, data: Dict[str, Any]) -> List[LintIssue]:
        issues = self._lint_common_fields(path, data)
        try:
            MemoryProduct.model_validate(data)
        except Exception as e:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="SCH002_MEMORY_SCHEMA_ERROR",
                    severity=LintSeverity.ERROR,
                    message=f"Memory schema validation failed: {e}",
                )
            )

        # Salience verification: 0.0 <= salience <= 1.0
        salience = data.get("salience")
        if salience is not None:
            if not isinstance(salience, (int, float)) or not (
                0.0 <= float(salience) <= 1.0
            ):
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="STR001_SALIENCE_BOUNDS",
                        severity=LintSeverity.ERROR,
                        message=f"Salience value '{salience}' must be a float between 0.0 and 1.0",
                        field_path="salience",
                    )
                )

        # 5-Kind Taxonomy & Scars
        mem_type = data.get("memory_type", data.get("episode_type", "incident"))
        valid_kinds = {"lore", "work", "incident", "relational", "telemetry"}
        if mem_type not in valid_kinds:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR009_INVALID_MEMORY_KIND",
                    severity=LintSeverity.ERROR,
                    message=(
                        f"Invalid memory_type '{mem_type}'. "
                        f"Must be one of: {sorted(valid_kinds)}"
                    ),
                    field_path="memory_type",
                )
            )

        scars = data.get("operational_scars")
        if not isinstance(scars, list):
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR002_SCARS_NOT_A_LIST",
                    severity=LintSeverity.ERROR,
                    message="'operational_scars' must be a list",
                    field_path="operational_scars",
                )
            )
        else:
            # Incident memories MUST have non-empty operational scars (concrete consequences)
            if mem_type == "incident" and len(scars) == 0:
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="STR002_EMPTY_SCARS_INCIDENT",
                        severity=LintSeverity.ERROR,
                        message=(
                            "Incident memories must document concrete operational scars or damages"
                        ),
                        field_path="operational_scars",
                    )
                )
            elif len(scars) == 0:
                # For non-incident memories, empty scars is allowed under 5-Kind Taxonomy
                pass

        # Lessons learned verification
        lessons = data.get("lessons_learned")
        if not isinstance(lessons, list) or len(lessons) == 0:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR003_EMPTY_LESSONS",
                    severity=LintSeverity.ERROR,
                    message="Memories must contain at least one distilled lesson learned",
                    field_path="lessons_learned",
                )
            )

        # Teleology verification inside memory manifest if present
        teleology = data.get("teleology")
        if teleology and isinstance(teleology, dict):
            if not teleology.get("primary_goal"):
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="STR005_TELEOLOGY_GOAL_MISSING",
                        severity=LintSeverity.WARNING,
                        message="Teleology should define a non-empty 'primary_goal'",
                        field_path="teleology.primary_goal",
                    )
                )

        return issues

    def _lint_lineage_dict(self, path: Path, data: Dict[str, Any]) -> List[LintIssue]:
        issues = self._lint_common_fields(path, data)
        try:
            LineageProduct.model_validate(data)
        except Exception as e:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="SCH003_LINEAGE_SCHEMA_ERROR",
                    severity=LintSeverity.ERROR,
                    message=f"Lineage schema validation failed: {e}",
                )
            )

        mem_ids = data.get("memory_ids", [])
        if not isinstance(mem_ids, list) or len(mem_ids) == 0:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR010_EMPTY_LINEAGE_MEMORIES",
                    severity=LintSeverity.ERROR,
                    message="Lineage must specify at least one member memory_id",
                    field_path="memory_ids",
                )
            )

        return issues

    def _lint_card_json(self, path: Path, raw_content: str) -> List[LintIssue]:
        issues: List[LintIssue] = []
        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="SYN002_JSON_SYNTAX",
                    severity=LintSeverity.ERROR,
                    message=f"JSON decoding error: {exc}",
                    line_number=exc.lineno,
                )
            )
            return issues

        if not isinstance(data, dict):
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR000_NOT_A_MAPPING",
                    severity=LintSeverity.ERROR,
                    message="card.json root must be a JSON object",
                )
            )
            return issues

        try:
            card = CatalogCard.model_validate(data)
        except Exception as e:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="SCH004_CARD_SCHEMA_ERROR",
                    severity=LintSeverity.ERROR,
                    message=f"Catalog card schema validation failed: {e}",
                )
            )
            return issues

        # Teleology completeness in card.json
        if not card.teleology:
            issues.append(
                LintIssue(
                    file_path=path,
                    rule_id="STR005_CARD_TELEOLOGY_MISSING",
                    severity=LintSeverity.ERROR,
                    message="Catalog card must define a 'teleology' block",
                    field_path="teleology",
                )
            )
        else:
            if not card.teleology.primary_goal:
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="STR005_CARD_PRIMARY_GOAL_MISSING",
                        severity=LintSeverity.ERROR,
                        message="Catalog card teleology must define 'primary_goal'",
                        field_path="teleology.primary_goal",
                    )
                )
            if not card.teleology.agent_drives:
                issues.append(
                    LintIssue(
                        file_path=path,
                        rule_id="STR005_CARD_AGENT_DRIVES_MISSING",
                        severity=LintSeverity.WARNING,
                        message="Catalog card teleology should specify at least one agent drive",
                        field_path="teleology.agent_drives",
                    )
                )

        return issues

    def lint_directory(self, dir_path: Path) -> LintResult:
        """Recursively scan a directory for all mnemonic manifests and cards."""
        result = LintResult(target=str(dir_path))
        if not dir_path.exists() or not dir_path.is_dir():
            result.issues.append(
                LintIssue(
                    file_path=dir_path,
                    rule_id="IO001_DIR_NOT_FOUND",
                    severity=LintSeverity.ERROR,
                    message=f"Target directory does not exist or is not a directory: {dir_path}",
                )
            )
            return result

        manifest_extensions = {".yaml", ".yml", ".json"}
        product_count = 0
        file_count = 0

        for path in sorted(dir_path.rglob("*")):
            if path.is_file() and path.suffix.lower() in manifest_extensions:
                file_count += 1
                if path.name.lower() in (
                    "persona.yaml",
                    "persona.yml",
                    "memory.yaml",
                    "memory.yml",
                    "lineage.yaml",
                    "lineage.yml",
                ):
                    product_count += 1

                file_issues = self.lint_file(path)
                result.issues.extend(file_issues)

        result.scanned_files = file_count
        result.scanned_products = product_count
        return result

    def lint_catalog(self, catalog_root: Optional[Path] = None) -> LintResult:
        """Lint the entire bundled or specified MnemoLink catalog."""
        root = catalog_root or get_bundled_catalog_root()
        res = self.lint_directory(root)
        res.target = f"Catalog ({root})"
        return res
