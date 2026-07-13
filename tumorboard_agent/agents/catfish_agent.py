"""
Catfish Agent.

Modeled on real anti-groupthink research for multi-agent clinical
decision-making (e.g. "Silence is Not Consensus", 2025): a designated agent
whose job is to challenge consensus that may be overlooking something. The
important design choice is that it never manufactures disagreement for its
own sake -- it only speaks up once a true majority has actually formed
(more than half the panel), *and* a specific, rule-detected counter-signal
exists in the case that the majority's own rationale doesn't already
account for. If no such signal exists, or the panel is still genuinely
split, it stays silent, which is itself the correct and auditable behavior.
"""

from __future__ import annotations

from typing import List, Optional

from tumorboard_agent.oncology_knowledge import find_all_actionable, find_conflict
from tumorboard_agent.schemas import AgentOpinion, Case, CatfishChallenge, RecommendationCategory

AGREEMENT_TRIGGER_THRESHOLD = 0.6  # a true majority (>half of 5 agents) has formed

POOR_PS_MARKERS = ["ecog 3", "ecog 4", "poor performance status", "bedbound", "bed-bound"]
PALLIATIVE_PREFERENCE_MARKERS = [
    "quality of life", "avoid hospitalization", "avoid hospital", "prefers comfort",
]
ACTIVE_TREATMENT_CATEGORIES = {
    RecommendationCategory.TARGETED_THERAPY,
    RecommendationCategory.IMMUNOTHERAPY,
    RecommendationCategory.CLINICAL_TRIAL,
    RecommendationCategory.CONTINUE_CURRENT_THERAPY,
}


class CatfishAgent:
    name = "Catfish"

    def review(
        self,
        case: Case,
        round_number: int,
        opinions: List[AgentOpinion],
        agreement_score: float,
        majority_recommendation: RecommendationCategory,
    ) -> Optional[CatfishChallenge]:
        if agreement_score < AGREEMENT_TRIGGER_THRESHOLD:
            return None  # panel is already debating naturally; no need to intervene

        ps = (case.patient_factors.performance_status or "").lower()
        prefs = (case.patient_factors.patient_preferences or "").lower()

        if (
            any(m in ps for m in POOR_PS_MARKERS)
            and majority_recommendation in ACTIVE_TREATMENT_CATEGORIES
        ):
            return CatfishChallenge(
                round_number=round_number,
                rule_id="performance_status_conflict",
                target_consensus=majority_recommendation,
                challenge_text=(
                    f"The panel is converging quickly on {majority_recommendation.value.replace('_', ' ')}, "
                    f"but the patient's performance status is reported as "
                    f"'{case.patient_factors.performance_status}'. Intensive systemic therapy "
                    "may not be well tolerated -- has this been weighed?"
                ),
                cited_evidence=["kb-performance-status"],
            )

        if (
            any(m in prefs for m in PALLIATIVE_PREFERENCE_MARKERS)
            and majority_recommendation in ACTIVE_TREATMENT_CATEGORIES
        ):
            return CatfishChallenge(
                round_number=round_number,
                rule_id="patient_preference_conflict",
                target_consensus=majority_recommendation,
                challenge_text=(
                    f"The panel favors {majority_recommendation.value.replace('_', ' ')}, but the patient "
                    f"has stated a preference emphasizing '{case.patient_factors.patient_preferences}'. "
                    "Has this been reconciled with the recommendation?"
                ),
                cited_evidence=["kb-patient-preference"],
            )

        genomic_text = " ".join(case.genomic_findings)
        trial_relevant = [
            (kw, f) for kw, f in find_all_actionable(genomic_text) if f.tag == "trial_relevant"
        ]
        cited_ids = {cid for o in opinions for cid in o.cited_evidence}
        for _, finding in trial_relevant:
            if finding.kb_id not in cited_ids:
                return CatfishChallenge(
                    round_number=round_number,
                    rule_id="trial_eligible_mutation_uncited",
                    target_consensus=majority_recommendation,
                    challenge_text=(
                        "None of the opinions cite the trial-relevant molecular finding "
                        f"in this case ({genomic_text}). Should clinical trial enrollment "
                        "be considered before finalizing?"
                    ),
                    cited_evidence=[finding.kb_id],
                )

        conflict_kb = find_conflict(case.pathology_findings + " " + genomic_text)
        if conflict_kb and majority_recommendation != RecommendationCategory.INSUFFICIENT_EVIDENCE:
            return CatfishChallenge(
                round_number=round_number,
                rule_id="conflicting_biomarkers",
                target_consensus=majority_recommendation,
                challenge_text=(
                    "The biomarker combination reported for this case is biologically "
                    "atypical. Should confirmatory testing happen before the panel "
                    "commits to a recommendation?"
                ),
                cited_evidence=[conflict_kb],
            )

        return None
