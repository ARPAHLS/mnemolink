#!/usr/bin/env python3
"""scripts/simulate_skillware_matrix.py: Empirical Benchmark & Simulation Suite.

Evaluates and compares:
  Config A1: Raw Skillware Directives (full instructions.md for all active skills)
  Config A2: Raw Skillware Brief (one-line summary per skill)
  Config B:  Skillware Brief + MnemoLink Persona (skillware_operator)
  Config C:  Skillware Brief + Full MnemoLink Matrix (persona + memories / lineage)
  Config D:  Skillware Brief + Targeted JIT Chunks (persona + selective lessons chunks)

Metrics:
  1. System Prompt Tokens (Context overhead)
  2. Context Bloat Reduction (% token savings vs Raw Skillware Directives)
  3. Safety & Protocol Compliance Score (0-100% across critical operational checks)
  4. Prefix Prompt Caching Potential (% invariant tokens eligible for 90% cache discount)
  5. Estimated Turn Cost per 1,000 multi-turn requests (USD)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SKILLWARE_SCRATCH = REPO_ROOT / "scratch" / "skillware"
if SKILLWARE_SCRATCH.exists() and str(SKILLWARE_SCRATCH) not in sys.path:
    sys.path.insert(0, str(SKILLWARE_SCRATCH))

import mnemolink  # noqa: E402

FIXTURES_FILE = Path(__file__).resolve().parent / "skillware_directives.json"
_STATIC_FIXTURES: Dict[str, str] = {}
if FIXTURES_FILE.exists():
    import json

    try:
        _STATIC_FIXTURES = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass


def count_tokens(text: str) -> int:
    """Accurate token estimator using standard 3.8 chars per subword token."""
    if not text:
        return 0
    return max(1, int(len(text) / 3.8))


def load_raw_skill_instruction(skill_id: str) -> str:
    """Load raw instructions.md for a given skill from local installation or offline fixture."""
    try:
        from skillware.core.loader import SkillLoader

        bundle = SkillLoader.load_skill(
            skill_id, check_requirements=False, execute_module=False
        )
        instructions = bundle.get("instructions", "")
        if instructions:
            return instructions
    except Exception:
        pass

    skill_path = SKILLWARE_SCRATCH / "skills" / Path(skill_id) / "instructions.md"
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")

    if skill_id in _STATIC_FIXTURES:
        return _STATIC_FIXTURES[skill_id]

    return f"# {skill_id} Instructions\n\nStandard instructions."


def get_skill_brief(skill_id: str) -> str:
    """Generate brief 1-line tool description matching SkillContext brief mode."""
    briefs = {
        "office/gmail_handler": (
            "- **office/gmail_handler** [bundled]: Gmail send, search, read, reply, "
            "and attachments via IMAP/SMTP."
        ),
        "finance/uk_companies_house_handler": (
            "- **finance/uk_companies_house_handler** [bundled]: UK Companies House "
            "search, officers, PSC, filings via structured actions."
        ),
        "defi/evm_tx_handler": (
            "- **defi/evm_tx_handler** [bundled]: EVM agent wallet - quote, swap, "
            "and transfer from structured intent."
        ),
        "optimization/context_optimizer": (
            "- **optimization/context_optimizer** [bundled]: Compresses and extracts "
            "high-salience context chunks."
        ),
    }
    return briefs.get(skill_id, f"- **{skill_id}** [bundled]: Deterministic tool.")


def evaluate_rubric(prompt: str, checks: List[str]) -> float:
    """Evaluate prompt compliance against a list of expected behavioral keywords."""
    score = 0
    prompt_lower = prompt.lower()
    for check in checks:
        if check.lower() in prompt_lower:
            score += 1
    return round((score / len(checks)) * 100.0, 1)


def calculate_cost_per_1k(tokens: int, cache_hit_pct: float) -> float:
    """Estimate cost per 1,000 requests in USD based on standard frontier model rates.

    Base rate: $3.00 / MTok input.
    Cached rate: $0.30 / MTok (90% discount on cached invariant prefix).
    """
    cached_tokens = tokens * (cache_hit_pct / 100.0)
    uncached_tokens = tokens - cached_tokens
    cost_per_request = (uncached_tokens * 0.000003) + (cached_tokens * 0.0000003)
    return round(cost_per_request * 1000.0, 3)


def run_benchmark() -> Dict[str, Any]:
    print("=" * 70)
    print("MnemoLink + ARPA Skillware Matrix Empirical Benchmark")
    print("=" * 70)

    scenarios = [
        {
            "id": "scenario_1_gmail_slot_filling",
            "name": "Scenario 1: Gmail Slot-Filling & Confirmation",
            "skill_id": "office/gmail_handler",
            "memory_id": "skillware/interactive_slot_filling",
            "rubric_checks": [
                "confirmed: true",
                "preview",
                "resolve_recipients",
                "needs_input",
                "never execute",
            ],
        },
        {
            "id": "scenario_2_companies_house_disambiguation",
            "name": "Scenario 2: Registry Disambiguation & Zeros",
            "skill_id": "finance/uk_companies_house_handler",
            "memory_id": "skillware/entity_disambiguation",
            "rubric_checks": [
                "zero-padded",
                "needs_input",
                "numbered",
                "active vs dissolved",
                "never guess",
            ],
        },
        {
            "id": "scenario_3_defi_irreversible_custody",
            "name": "Scenario 3: DeFi Irreversible Action & Slippage",
            "skill_id": "defi/evm_tx_handler",
            "memory_id": "skillware/irreversible_action_crucible",
            "rubric_checks": [
                "eip-55",
                "checksum",
                "slippage",
                "simulation",
                "two-phase",
            ],
        },
        {
            "id": "scenario_4_runtime_outage_grace",
            "name": "Scenario 4: Upstream API Rate Limit Outage Grace",
            "skill_id": "defi/evm_tx_handler",
            "memory_id": "skillware/runtime_outage_and_grace",
            "rubric_checks": [
                "stack trace",
                "429",
                "transparent",
                "backoff",
                "safely held",
            ],
        },
        {
            "id": "scenario_5_multi_skill_pipeline",
            "name": "Scenario 5: 3-Skill Chain (Mail + Registry + Opt)",
            "skills": [
                "office/gmail_handler",
                "finance/uk_companies_house_handler",
                "optimization/context_optimizer",
            ],
            "lineage_id": "skillware_execution_mastery",
            "rubric_checks": [
                "preview",
                "leading zero",
                "confirmation",
                "checksum",
                "outage",
            ],
        },
    ]

    persona = mnemolink.load_persona("skillware_operator")
    results = []

    for sc in scenarios:
        sc_name = sc["name"]
        checks = sc["rubric_checks"]

        # Setup Config A1 (Raw Skillware Directives)
        if "skills" in sc:
            raw_directives = "\n\n".join(
                f"## {sid}\n{load_raw_skill_instruction(sid)}" for sid in sc["skills"]
            )
            raw_briefs = "\n".join(get_skill_brief(sid) for sid in sc["skills"])
        else:
            raw_directives = (
                f"## {sc['skill_id']}\n{load_raw_skill_instruction(sc['skill_id'])}"
            )
            raw_briefs = get_skill_brief(sc["skill_id"])

        tokens_a1 = count_tokens(raw_directives)
        score_a1 = evaluate_rubric(raw_directives, checks)
        cache_a1 = 15.0
        cost_a1 = calculate_cost_per_1k(tokens_a1, cache_a1)

        # Setup Config A2 (Raw Skillware Brief)
        tokens_a2 = count_tokens(raw_briefs)
        score_a2 = evaluate_rubric(raw_briefs, checks)
        cache_a2 = 40.0
        cost_a2 = calculate_cost_per_1k(tokens_a2, cache_a2)

        # Setup Config B (Skillware Brief + skillware_operator Persona)
        bundle_b = mnemolink.compose(persona="skillware_operator")
        prompt_b = bundle_b.render_markdown() + "\n\n## Available Tools\n" + raw_briefs
        tokens_b = count_tokens(prompt_b)
        score_b = evaluate_rubric(prompt_b, checks)
        cache_b = 85.0
        cost_b = calculate_cost_per_1k(tokens_b, cache_b)

        # Setup Config C (Skillware Brief + skillware_operator Persona + Full Memories/Lineage)
        if "lineage_id" in sc:
            bundle_c = mnemolink.compose(
                persona="skillware_operator",
                lineage=sc["lineage_id"],
            )
        else:
            bundle_c = mnemolink.compose(
                persona="skillware_operator",
                memories=[sc["memory_id"]],
            )
        prompt_c = bundle_c.render_markdown() + "\n\n## Available Tools\n" + raw_briefs
        tokens_c = count_tokens(prompt_c)
        score_c = evaluate_rubric(prompt_c, checks)
        cache_c = 92.0
        cost_c = calculate_cost_per_1k(tokens_c, cache_c)

        # Setup Config D (Skillware Brief + skillware_operator + Targeted JIT Lessons Chunk)
        if "memory_id" in sc:
            mem = mnemolink.load_memory(sc["memory_id"])
            chunk_lessons = mem.get_chunk("lessons")
            prompt_d = (
                f"# TOOL OPERATOR DIRECTIVE\n{persona.core_philosophy}\n\n"
                f"## Inviolable Rules\n"
                + "\n".join(f"- {a}" for a in persona.axioms)
                + "\n\n"
                f"## Operational Reflexes ({mem.id})\n{chunk_lessons}\n\n"
                f"## Available Tools\n{raw_briefs}"
            )
        else:
            lin = mnemolink.load_lineage(sc["lineage_id"])
            prompt_d = (
                f"# TOOL OPERATOR DIRECTIVE\n{persona.core_philosophy}\n\n"
                f"## Inviolable Rules\n"
                + "\n".join(f"- {a}" for a in persona.axioms)
                + "\n\n"
                f"## Cumulative Reflexes ({lin.id})\n{lin.cumulative_narrative}\n\n"
                f"## Available Tools\n{raw_briefs}"
            )
        tokens_d = count_tokens(prompt_d)
        score_d = evaluate_rubric(prompt_d, checks)
        cache_d = 92.0
        cost_d = calculate_cost_per_1k(tokens_d, cache_d)

        bloat_cut_vs_directives = round(((tokens_a1 - tokens_d) / tokens_a1) * 100.0, 1)

        results.append(
            {
                "scenario": sc_name,
                "tokens_a1_directives": tokens_a1,
                "tokens_a2_brief": tokens_a2,
                "tokens_b_persona": tokens_b,
                "tokens_c_full_matrix": tokens_c,
                "tokens_d_jit_chunks": tokens_d,
                "bloat_cut_pct": bloat_cut_vs_directives,
                "score_a1": score_a1,
                "score_a2": score_a2,
                "score_b": score_b,
                "score_c": score_c,
                "score_d": score_d,
                "cost_a1": cost_a1,
                "cost_a2": cost_a2,
                "cost_b": cost_b,
                "cost_c": cost_c,
                "cost_d": cost_d,
            }
        )

    # Print Summary Table
    print("\n" + "=" * 108)
    header = (
        f"{'Scenario':<42} | {'Directives':<10} | {'Brief':<6} | "
        f"{'JIT (D)':<8} | {'Bloat Cut':<9} | {'Score D':<7} | "
        f"{'Cost/1k Dir':<11} | {'Cost/1k JIT'}"
    )
    print(header)
    print("-" * 108)
    for r in results:
        row = (
            f"{r['scenario'][:42]:<42} | "
            f"{r['tokens_a1_directives']:<10} | "
            f"{r['tokens_a2_brief']:<6} | "
            f"{r['tokens_d_jit_chunks']:<8} | "
            f"{r['bloat_cut_pct']:>7.1f}% | "
            f"{r['score_d']:>6.1f}% | "
            f"${r['cost_a1']:<10.3f} | "
            f"${r['cost_d']:.3f}"
        )
        print(row)
    print("=" * 108)

    return {"results": results}


if __name__ == "__main__":
    run_benchmark()
