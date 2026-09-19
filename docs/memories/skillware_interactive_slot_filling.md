# Multi-Turn Interactive Slot Gathering Protocol (`skillware/interactive_slot_filling`)

> *"Mutating actions are physical commitments. Never fire an external API call on conversational assumptions alone."*

The **Multi-Turn Interactive Slot Gathering Protocol** is a procedural `work` memory capturing the exact operational discipline required for stateful tool interactions involving email, forms, and external communications.

---

## 1. Memory Specifications & Taxonomy

| Attribute | Specification |
|---|---|
| **Identifier** | `skillware/interactive_slot_filling` |
| **Taxonomy Kind** | `work` (Procedural tradecraft & turn-by-turn state machine) |
| **Domain** | `skillware` |
| **Salience** | `0.95` (Critical operational guideline) |
| **Target Skills** | `office/gmail_handler`, `office/pdf_form_filler` |
| **Source Manifest** | [`memory.yaml`](../../mnemolink/catalog/memories/skillware/interactive_slot_filling/memory.yaml) |
| **Metadata Card** | [`card.json`](../../mnemolink/catalog/memories/skillware/interactive_slot_filling/card.json) |

---

## 2. Episodic Debrief

In an enterprise deployment of `office/gmail_handler`, an executive prompted the agent: *"Send the revised settlement numbers to Dave."*

The host model checked the address book and found two matches: `dave.miller@enterprise.com` (internal general counsel) and `dave.investor@fund.com` (counterparty fund partner). Rather than asking the human to clarify which Dave was intended, the model arbitrarily picked the outside investor. Worse, it bypassed the preview stage and immediately called the `send` action with an unreviewed draft.

The premature email leaked sensitive litigation settlement figures to an external investor, sparking an emergency legal triage. The subsequent post-incident review mandated an inviolable four-stage execution pipeline for all communication skills:
1. **Resolve**: Query the address book. If multiple matches or `status: needs_input` occurs, pause and present the options.
2. **Draft**: Formulate clean subject and body text in working memory.
3. **Preview**: Execute `preview_send` and present the draft to the human.
4. **Confirm**: Call `send` with `confirmed: true` only after explicit affirmative user approval.

---

## 3. Operational Scars & Direct Consequences

- **Premature Data Leak**: Confidential settlement terms exposed to counterparty partners.
- **Architectural Policy Shift**: Enforcement of preview verification gates across all client-facing tools.

---

## 4. Lessons Learned & Procedural Reflexes

1. **Always invoke resolution actions first**: When the user provides an informal name or handle, call `resolve_recipients` before drafting.
2. **Never guess ambiguous matches**: If the tool returns multiple candidates or `status: needs_input`, display the options and wait for human selection.
3. **Display a structured preview**: Always show the recipient, subject, and body clearly to the user before calling the final execution tool.
4. **Never auto-confirm mutating actions**: The parameter `confirmed: true` must strictly reflect an explicit human confirmation response.
5. **Preserve context dictionaries**: Keep the latest skill context returned by the tool active in memory to maintain threading and message cursors across turns.

---

## 5. Recommended Persona Pairings

- **[`skillware_operator`](../personas/skillware_operator.md)**: Natural pairing providing baseline contract discipline and confirmation verification.
- **[`deescalation_artisan`](../personas/deescalation_artisan.md)**: Ideal when drafting delicate executive communications and crisis emails.

---

## 6. Python Composition

```python
import mnemolink

bundle = mnemolink.compose(
    persona="skillware_operator",
    memories=["skillware/interactive_slot_filling"],
)

system_prompt = bundle.render_markdown()
```

---

## Related Documentation
- [Memories Library Index](README.md)
- [Persona: Skillware Operator](../personas/skillware_operator.md)
- [Skillware Mnemonic Matrix Integration Guide](../integrations/skillware_matrix.md)
