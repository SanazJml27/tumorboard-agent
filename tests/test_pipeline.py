import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tumorboard_agent.orchestrator import TumorBoardOrchestrator
from tumorboard_agent.schemas import Case, EscalationTier, PatientFactors, RecommendationCategory
from tumorboard_agent.oncology_knowledge import find_actionable, find_conflict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_case(case_id: str) -> Case:
    with open(DATA_DIR / "synthetic_cases.json", "r", encoding="utf-8") as f:
        cases = {c["case_id"]: c for c in json.load(f)}
    return Case(**cases[case_id])


def test_actionable_finding_lookup():
    finding = find_actionable("EGFR exon 19 deletion")
    assert finding is not None
    assert finding.recommendation == RecommendationCategory.TARGETED_THERAPY


def test_conflict_combination_detected_only_when_both_present():
    assert find_conflict("MSI-H by IHC") is None
    assert find_conflict("MSI-H by IHC, TMB-low on panel") is not None


def test_case_001_her2_reaches_senior_review_no_catfish():
    orchestrator = TumorBoardOrchestrator()
    report = orchestrator.run(load_case("case-001"))
    assert report.consensus.final_recommendation == RecommendationCategory.TARGETED_THERAPY
    assert report.oversight.tier == EscalationTier.SENIOR_REVIEW
    assert report.consensus.catfish_intervened is False


def test_case_002_catfish_flips_consensus_toward_palliative_care():
    orchestrator = TumorBoardOrchestrator()
    report = orchestrator.run(load_case("case-002"))
    assert report.consensus.catfish_intervened is True
    assert report.consensus.final_recommendation == RecommendationCategory.PALLIATIVE_SUPPORTIVE_CARE
    assert any(
        r.catfish_challenge and r.catfish_challenge.rule_id == "performance_status_conflict"
        for r in report.rounds
    )


def test_case_004_catfish_flags_uncited_trial_mutation():
    orchestrator = TumorBoardOrchestrator()
    report = orchestrator.run(load_case("case-004"))
    assert report.consensus.catfish_intervened is True
    assert any(
        r.catfish_challenge and r.catfish_challenge.rule_id == "trial_eligible_mutation_uncited"
        for r in report.rounds
    )


def test_case_006_insufficient_evidence_triggers_urgent_escalation():
    orchestrator = TumorBoardOrchestrator()
    report = orchestrator.run(load_case("case-006"))
    assert report.consensus.final_recommendation == RecommendationCategory.INSUFFICIENT_EVIDENCE
    assert report.oversight.tier == EscalationTier.URGENT_ESCALATION


def test_case_007_clean_unanimous_case_auto_finalizes():
    orchestrator = TumorBoardOrchestrator()
    report = orchestrator.run(load_case("case-007"))
    assert report.consensus.catfish_intervened is False
    assert report.consensus.dissenting_agents == []
    assert report.oversight.tier == EscalationTier.AUTO_FINALIZE


def test_full_battery_matches_eval_gold():
    with open(DATA_DIR / "eval_gold.json", "r", encoding="utf-8") as f:
        gold = json.load(f)
    orchestrator = TumorBoardOrchestrator()
    for g in gold:
        report = orchestrator.run(load_case(g["case_id"]))
        assert report.consensus.final_recommendation.value == g["expected_recommendation"], g["case_id"]
        assert report.oversight.tier.value == g["expected_tier"], g["case_id"]
        assert report.consensus.catfish_intervened == g["expected_catfish"], g["case_id"]


def test_catfish_stays_silent_when_no_counter_signal():
    """A patient with fine performance status and no special conflicts should
    not trigger a catfish challenge even if a majority forms quickly."""
    case = Case(
        case_id="synthetic-silent-test",
        cancer_type="lung",
        imaging_findings="Follow-up imaging shows stable disease with no new lesions.",
        pathology_findings="Adenocarcinoma. NGS panel reveals EGFR exon 19 deletion.",
        genomic_findings=["EGFR exon 19 deletion"],
        patient_factors=PatientFactors(performance_status="ECOG 0", patient_preferences="No special concerns."),
    )
    orchestrator = TumorBoardOrchestrator()
    report = orchestrator.run(case)
    assert report.consensus.catfish_intervened is False
