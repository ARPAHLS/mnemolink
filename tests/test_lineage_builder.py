"""Unit tests for the dynamic LineageBuilder and lego-brick chaining."""

from mnemolink.lineage import LineageBuilder
from mnemolink.models import MemoryProduct, PersonaProduct


def test_lineage_builder_synthesis():
    persona = PersonaProduct(
        id="test_craftsman",
        name="Test Craftsman",
        core_philosophy="Measure twice, cut once.",
        self_narrative="I build things that endure.",
    )

    mem1 = MemoryProduct(
        id="woodwork/measurement_error",
        name="The Bent Joist Catastrophe",
        domain="construction",
        episode_debrief="Cut joist 2 inches short, causing roof sag.",
        operational_scars=["Replaced entire timber frame at personal cost."],
        lessons_learned=["Always verify laser level before making the final cut."],
    )

    mem2 = MemoryProduct(
        id="woodwork/joinery_triumph",
        name="Mortise and Tenon Restoration",
        domain="construction",
        episode_debrief="Hand-cut joinery withstood gale-force winds.",
        lessons_learned=[
            "Traditional friction joinery outlasts modern chemical adhesives."
        ],
    )

    builder = LineageBuilder(persona=persona)
    lineage = builder.build([mem1, mem2], lineage_id="carpentry_evolution")

    assert lineage.id == "carpentry_evolution"
    assert len(lineage.memory_ids) == 2
    assert len(lineage.chronology) == 2
    assert len(lineage.causal_bridges) == 1
    assert "Bent Joist Catastrophe" in lineage.cumulative_narrative
    assert "Mortise and Tenon Restoration" in lineage.cumulative_narrative
    assert "laser level" in lineage.causal_bridges[0].lower()


def test_lineage_builder_empty():
    builder = LineageBuilder()
    lineage = builder.build([])
    assert lineage.id == "dynamic_lineage"
    assert len(lineage.memory_ids) == 0
    assert lineage.cumulative_narrative == ""
