# Third-Party Outage and Operational Grace (`skillware/runtime_outage_and_grace`)

> *"Transport failure is not a catastrophic software crash. Calm, transparent communication protects user confidence when infrastructure throttles."*

The **Third-Party Outage and Operational Grace** memory is a `relational` memory establishing how autonomous agents should communicate and behave during external API rate limits (HTTP 429), gateway timeouts (HTTP 504), and upstream maintenance (HTTP 503).

---

## 1. Memory Specifications & Taxonomy

| Attribute | Specification |
|---|---|
| **Identifier** | `skillware/runtime_outage_and_grace` |
| **Taxonomy Kind** | `relational` (User de-escalation & operational resilience) |
| **Domain** | `skillware` |
| **Salience** | `0.88` (High operational importance) |
| **Target Skills** | All REST / RPC / IMAP API-dependent skills |
| **Source Manifest** | [`memory.yaml`](../../mnemolink/catalog/memories/skillware/runtime_outage_and_grace/memory.yaml) |
| **Metadata Card** | [`card.json`](../../mnemolink/catalog/memories/skillware/runtime_outage_and_grace/card.json) |

---

## 2. Episodic Debrief

During an active market trading session, an upstream Ethereum JSON-RPC provider experienced temporary network congestion, returning HTTP 429 Too Many Requests followed by HTTP 503 Service Unavailable.

The autonomous agent panicked and dumped a 42-line raw Python traceback into the user chat with the alarming banner: `FATAL: Wallet transport crashed. Process aborted.`

The client assumed their funds had been compromised or stolen, initiating emergency escalations to executive leadership. In reality, the upstream node had merely throttled requests for 15 seconds.

The incident review mandated that external transport failures must never be reported as fatal software bugs. Agents must shield raw stack traces, reassure users with clear operational status updates, implement jittered exponential backoff, and offer constructive next steps.

---

## 3. Operational Scars & Direct Consequences

- **Executive Escalation**: Four hours of emergency support and client relationship repair following an alarming 429 error dump.
- **Client Anxiety**: Temporary loss of user trust in automated systems due to unhandled raw transport traces.

---

## 4. Lessons Learned & Procedural Reflexes

1. **Never output raw stack traces**: Shield end users from raw JSON dumps, tracebacks, or socket errors.
2. **Translate HTTP codes into human updates**: Explain that the upstream service is temporarily experiencing high traffic.
3. **Reassure state preservation**: Confirm that the user's intent and parameters are held safely in memory and will be retried automatically.
4. **Offer constructive alternatives**: If an outage persists, suggest manual fallback links or alternative data sources rather than unhelpful dead ends.

---

## 5. Recommended Persona Pairings

- **[`skillware_operator`](../personas/skillware_operator.md)**: Baseline tool execution and resilience.
- **[`deescalation_artisan`](../personas/deescalation_artisan.md)**: Master-class empathy and panic reduction during enterprise incidents.

---

## 6. Python Composition

```python
import mnemolink

bundle = mnemolink.compose(
    persona="skillware_operator",
    memories=["skillware/runtime_outage_and_grace"],
)

system_prompt = bundle.render_markdown()
```

---

## Related Documentation
- [Memories Library Index](README.md)
- [Persona: Skillware Operator](../personas/skillware_operator.md)
- [Skillware Mnemonic Matrix Integration Guide](../integrations/skillware_matrix.md)
