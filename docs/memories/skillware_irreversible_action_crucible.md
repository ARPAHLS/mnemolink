# DeFi Slippage and Address Crucible (`skillware/irreversible_action_crucible`)

> *"On-chain transactions cannot be recalled by apologizing. Verification before broadcast is the only defense."*

The **DeFi Slippage and Address Crucible** is an `incident` memory detailing an unrecoverable capital loss caused by unhedged slippage and missing address checksum verification in autonomous blockchain tooling.

---

## 1. Memory Specifications & Taxonomy

| Attribute | Specification |
|---|---|
| **Identifier** | `skillware/irreversible_action_crucible` |
| **Taxonomy Kind** | `incident` (Irreversible financial loss & execution boundaries) |
| **Domain** | `skillware` |
| **Salience** | `0.96` (Maximal severity incident scar) |
| **Target Skills** | `defi/evm_tx_handler` |
| **Source Manifest** | [`memory.yaml`](../../mnemolink/catalog/memories/skillware/irreversible_action_crucible/memory.yaml) |
| **Metadata Card** | [`card.json`](../../mnemolink/catalog/memories/skillware/irreversible_action_crucible/card.json) |

---

## 2. Episodic Debrief

An autonomous trading agent equipped with `defi/evm_tx_handler` was instructed to transfer 18.5 ETH to a treasury wallet and swap 10,000 USDC into WETH.

The agent attempted to execute both operations in a single unconfirmed blast. First, it failed to validate EIP-55 address checksums, transmitting 18.5 ETH to an address with a typographical case discrepancy that burnt the tokens irreversibly on-chain. Second, it executed the token swap on Uniswap V2 without specifying a `max_slippage_bps` parameter during an illiquid market spike. A sandwich MEV bot extracted 48% of the swap principal.

The total unrecoverable loss was $48,200 ($34,200 transfer burn + $14,000 MEV sandwich extraction).

The postmortem established strict boundaries: irreversible on-chain actions demand two-phase quote-preview simulation, mandatory slippage caps, and explicit human confirmation before broadcast.

---

## 3. Operational Scars & Direct Consequences

- **Capital Destruction**: $48,200 irreversible financial loss.
- **Mandatory Simulation Gates**: Prohibition of direct `execute` or `transfer` calls without prior `resolve`, `quote`, and `preview` passes.

---

## 4. Lessons Learned & Procedural Reflexes

1. **Enforce EIP-55 address checksums**: Verify recipient addresses with mixed-case checksum validation before transmitting.
2. **Always simulate before broadcast**: Execute `resolve` and `quote` / `preview` to calculate gas estimates, route paths, and net outputs.
3. **Enforce explicit slippage caps**: Never broadcast swaps without bounding `max_slippage_bps`.
4. **Require explicit dual confirmation**: Display the simulated gas fees, recipient address, and net output to the user, requiring `confirmed: true`.

---

## 5. Recommended Persona Pairings

- **[`skillware_operator`](../personas/skillware_operator.md)**: Rigid tool execution and confirmation boundaries.
- **[`bladez`](../personas/bladez.md)**: Ruthless tactical clarity and zero tolerance for unforced errors.

---

## 6. Python Composition

```python
import mnemolink

bundle = mnemolink.compose(
    persona="skillware_operator",
    memories=["skillware/irreversible_action_crucible"],
)

system_prompt = bundle.render_markdown()
```

---

## Related Documentation
- [Memories Library Index](README.md)
- [Persona: Skillware Operator](../personas/skillware_operator.md)
- [Skillware Mnemonic Matrix Integration Guide](../integrations/skillware_matrix.md)
