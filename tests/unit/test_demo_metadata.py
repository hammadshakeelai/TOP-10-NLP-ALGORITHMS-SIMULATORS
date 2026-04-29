"""
Tests for demo metadata presence and correctness across all 13 simulators.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "packages"))
sys.path.insert(0, str(ROOT / "services" / "classical-nlp-service"))
sys.path.insert(0, str(ROOT / "services" / "transformer-service"))


# ── Classical ────────────────────────────────────────────────────────────────

def _get_classical_demo(name: str):
    from simulators.demo_metadata import CLASSICAL_DEMO_METADATA
    return CLASSICAL_DEMO_METADATA.get(name)


def _get_transformer_demo(name: str):
    import importlib.util
    _path = ROOT / "services" / "transformer-service" / "simulators" / "demo_metadata.py"
    _spec = importlib.util.spec_from_file_location("_transformer_demo_metadata", _path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    return _mod.TRANSFORMER_DEMO_METADATA.get(name)


CLASSICAL_IDS = ["tokenization", "tfidf", "naive_bayes", "svm", "rake", "textrank"]
TRANSFORMER_IDS = ["word_embeddings", "lstm", "transformer_attention", "bert", "gpt", "t5", "fasttext"]

# ── Existence tests ──────────────────────────────────────────────────────────

def test_all_classical_demo_metadata_present():
    for algo_id in CLASSICAL_IDS:
        demo = _get_classical_demo(algo_id)
        assert demo is not None, f"Missing classical demo metadata for '{algo_id}'"


def test_all_transformer_demo_metadata_present():
    for algo_id in TRANSFORMER_IDS:
        demo = _get_transformer_demo(algo_id)
        assert demo is not None, f"Missing transformer demo metadata for '{algo_id}'"


# ── Content tests ────────────────────────────────────────────────────────────

def test_classical_demo_metadata_has_required_fields():
    for algo_id in CLASSICAL_IDS:
        demo = _get_classical_demo(algo_id)
        assert demo.demo_input, f"{algo_id}: demo_input must be non-empty"
        assert demo.auto_parameters is not None, f"{algo_id}: auto_parameters must be present"
        assert demo.beginner_explanation, f"{algo_id}: beginner_explanation must be non-empty"
        assert demo.advanced_explanation, f"{algo_id}: advanced_explanation must be non-empty"
        assert len(demo.formula_cards) > 0, f"{algo_id}: must have at least 1 formula card"
        assert len(demo.step_explanations) > 0, f"{algo_id}: must have at least 1 step explanation"
        assert len(demo.references) > 0, f"{algo_id}: must have at least 1 reference"
        assert len(demo.receiver_mode_explanations) == 5, f"{algo_id}: must have explanations for all 5 receiver modes"
        assert demo.research_context, f"{algo_id}: research_context must be non-empty"
        assert demo.teaching_notes is not None, f"{algo_id}: teaching_notes must be present"


def test_transformer_demo_metadata_has_required_fields():
    for algo_id in TRANSFORMER_IDS:
        demo = _get_transformer_demo(algo_id)
        assert demo.demo_input, f"{algo_id}: demo_input must be non-empty"
        assert demo.auto_parameters is not None, f"{algo_id}: auto_parameters must be present"
        assert demo.beginner_explanation, f"{algo_id}: beginner_explanation must be non-empty"
        assert demo.advanced_explanation, f"{algo_id}: advanced_explanation must be non-empty"
        assert len(demo.formula_cards) > 0, f"{algo_id}: must have at least 1 formula card"
        assert len(demo.step_explanations) > 0, f"{algo_id}: must have at least 1 step explanation"
        assert len(demo.references) > 0, f"{algo_id}: must have at least 1 reference"
        assert len(demo.receiver_mode_explanations) == 5, f"{algo_id}: must have explanations for all 5 receiver modes"
        assert demo.research_context, f"{algo_id}: research_context must be non-empty"
        assert demo.teaching_notes is not None, f"{algo_id}: teaching_notes must be present"


def test_receiver_modes_cover_all_five():
    from shared_schemas import ReceiverMode
    expected = {ReceiverMode.BEGINNER, ReceiverMode.STUDENT, ReceiverMode.RESEARCHER,
                ReceiverMode.ENGINEER, ReceiverMode.INSTRUCTOR}
    for algo_id in CLASSICAL_IDS:
        demo = _get_classical_demo(algo_id)
        actual = {e.mode for e in demo.receiver_mode_explanations}
        assert actual == expected, f"{algo_id}: receiver modes mismatch: {actual}"
    for algo_id in TRANSFORMER_IDS:
        demo = _get_transformer_demo(algo_id)
        actual = {e.mode for e in demo.receiver_mode_explanations}
        assert actual == expected, f"{algo_id}: receiver modes mismatch: {actual}"


def test_formula_cards_have_required_fields():
    for algo_id in CLASSICAL_IDS:
        demo = _get_classical_demo(algo_id)
        for card in demo.formula_cards:
            assert card.title, f"{algo_id}: formula card missing title"
            assert card.formula, f"{algo_id}: formula card missing formula"
            assert card.explanation, f"{algo_id}: formula card missing explanation"


def test_step_explanations_have_required_fields():
    for algo_id in CLASSICAL_IDS:
        demo = _get_classical_demo(algo_id)
        for step in demo.step_explanations:
            assert step.step_id, f"{algo_id}: step missing step_id"
            assert step.stage, f"{algo_id}: step missing stage"
            assert step.title, f"{algo_id}: step missing title"
            assert step.description, f"{algo_id}: step missing description"


def test_references_are_real_papers():
    """Ensure references have enough info to find the paper (DOI, arxiv, or URL)."""
    for algo_id in CLASSICAL_IDS + TRANSFORMER_IDS:
        if algo_id in CLASSICAL_IDS:
            demo = _get_classical_demo(algo_id)
        else:
            demo = _get_transformer_demo(algo_id)
        for ref in demo.references:
            has_link = any([ref.doi, ref.arxiv_id, ref.url])
            assert ref.title, f"{algo_id}: reference missing title"
            assert has_link or ref.authors, f"{algo_id}: reference '{ref.title}' has no doi/arxiv/url or authors"


# ── Simulator DEMO_METADATA wiring tests ─────────────────────────────────────

def test_classical_simulators_have_demo_metadata_wired():
    import importlib.util
    service_dir = ROOT / "services" / "classical-nlp-service"
    sys.path.insert(0, str(service_dir))

    spec = importlib.util.spec_from_file_location("classical_registry", service_dir / "registry.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for algo_id in CLASSICAL_IDS:
        sim = mod.get_simulator(algo_id)
        assert sim.DEMO_METADATA is not None, f"{algo_id}: simulator DEMO_METADATA not set"
        assert sim.get_demo_metadata() is not None, f"{algo_id}: get_demo_metadata() returned None"


def test_classical_run_response_includes_demo_fields():
    import importlib.util
    service_dir = ROOT / "services" / "classical-nlp-service"
    sys.path.insert(0, str(service_dir))

    spec = importlib.util.spec_from_file_location("classical_registry2", service_dir / "registry.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from shared_schemas import RunRequest, AlgorithmID, TraceLevel
    sim = mod.get_simulator(AlgorithmID.TOKENIZATION)
    req = RunRequest(algorithm_id=AlgorithmID.TOKENIZATION, text="hello world test", trace_level=TraceLevel.SUMMARY)
    resp = sim.execute(req)

    assert len(resp.step_explanations) > 0, "RunResponse missing step_explanations"
    assert len(resp.formula_cards) > 0, "RunResponse missing formula_cards"
    assert len(resp.references) > 0, "RunResponse missing references"
    assert len(resp.receiver_mode_explanations) == 5, "RunResponse missing receiver_mode_explanations"
    assert resp.research_context, "RunResponse missing research_context"
    assert resp.teaching_notes is not None, "RunResponse missing teaching_notes"
