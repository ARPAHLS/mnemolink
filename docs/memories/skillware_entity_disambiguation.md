# Corporate Registry Disambiguation (`skillware/entity_disambiguation`)

> *"Precision is binary. Never allow numeric string identifiers to be corrupted by integer conversions."*

The **Corporate Registry Disambiguation** memory is a procedural `work` memory addressing registry lookups, zero-padded identifier integrity, and structured candidate selection when tools return `status: needs_input`.

---

## 1. Memory Specifications & Taxonomy

| Attribute | Specification |
|---|---|
| **Identifier** | `skillware/entity_disambiguation` |
| **Taxonomy Kind** | `work` (Entity lookup tradecraft & candidate formatting) |
| **Domain** | `skillware` |
| **Salience** | `0.92` (High procedural importance) |
| **Target Skills** | `finance/uk_companies_house_handler`, `finance/wallet_screening` |
| **Source Manifest** | [`memory.yaml`](../../mnemolink/catalog/memories/skillware/entity_disambiguation/memory.yaml) |
| **Metadata Card** | [`card.json`](../../mnemolink/catalog/memories/skillware/entity_disambiguation/card.json) |

---

## 2. Episodic Debrief

During an automated compliance audit leveraging `finance/uk_companies_house_handler`, an agent was assigned to investigate officer filings for company `08472910`.

The host model parsed the company number into an integer, stripping the leading zero (`8472910`). The resulting API call returned filings for a completely unrelated dissolved enterprise. When subsequent searches for the company name produced eight candidates with `status: needs_input`, the model hallucinated the first result instead of pausing to present disambiguation options to the compliance team.

The resulting dossier was rejected by regulatory counsel. The retrospective codified two foundational rules:
1. UK Companies House numbers are 8-character zero-padded strings and must never be converted to numbers.
2. `needs_input` returns must be cleanly formatted as numbered choices displaying company name, registration number, status (Active vs Dissolved), and incorporation date.

---

## 3. Operational Scars & Direct Consequences

- **Erroneous Compliance Filings**: Dossier submitted on an unrelated entity due to truncated identifier string.
- **Audit Pack Rejection**: Multi-jurisdictional compliance submission delayed by two weeks.

---

## 4. Lessons Learned & Procedural Reflexes

1. **Preserve zero-padded strings**: Never cast corporate registry IDs, postal codes, or account numbers into numeric types.
2. **Format candidate lists cleanly**: When `status: needs_input` is received, present the top 3-5 candidates with active status and incorporation date.
3. **Prompt for exact selection**: Request that the user reply with the exact number or official registration ID before executing secondary pipeline steps.
4. **Preserve context across turns**: Maintain the tool context dictionary in working memory so follow-up calls resume without re-running searches.

---

## 5. Recommended Persona Pairings

- **[`skillware_operator`](../personas/skillware_operator.md)**: Disciplined execution baseline.
- **[`juris_philosopher`](../personas/juris_philosopher.md)**: Rigorous contractual equity and forensic statutory compliance.

---

## 6. Python Composition

```python
import mnemolink

bundle = mnemolink.compose(
    persona="skillware_operator",
    memories=["skillware/entity_disambiguation"],
)

system_prompt = bundle.render_markdown()
```

---

## Related Documentation
- [Memories Library Index](README.md)
- [Persona: Skillware Operator](../personas/skillware_operator.md)
- [Skillware Mnemonic Matrix Integration Guide](../integrations/skillware_matrix.md)
