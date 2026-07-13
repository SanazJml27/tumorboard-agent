"""
Nurse Navigator Agent.

Represents patient-centered factors: performance status, comorbidities, and
stated preferences. Its job is not to diagnose biology but to flag when the
patient's fitness or values might not align with an intensive treatment
path -- exactly the kind of signal the catfish agent looks for when other
agents converge quickly on an aggressive recommendation.
"""

from __future__ import annotations

from tumorboard_agent.agents.base_specialist import BaseSpecialistAgent
from tumorboard_agent.schemas import AgentOpinion, Case, RecommendationCategory

POOR_PS_MARKERS = ["ecog 3", "ecog 4", "poor performance status", "bedbound", "bed-bound"]
PALLIATIVE_PREFERENCE_MARKERS = [
    "quality of life", "avoid hospitalization", "avoid hospital", "prefers comfort",
]


class NurseNavigatorAgent(BaseSpecialistAgent):
    name = "NurseNavigator"

    def initial_opinion(self, case: Case) -> AgentOpinion:
        ps = (case.patient_factors.performance_status or "").lower()
        prefs = (case.patient_factors.patient_preferences or "").lower()
        facts = []
        citations = ["kb-performance-status"]

        if any(m in ps for m in POOR_PS_MARKERS):
            recommendation = RecommendationCategory.PALLIATIVE_SUPPORTIVE_CARE
            confidence = 0.75
            facts.append(f"Performance status reported as: '{case.patient_factors.performance_status}'.")
        elif any(m in prefs for m in PALLIATIVE_PREFERENCE_MARKERS):
            recommendation = RecommendationCategory.PALLIATIVE_SUPPORTIVE_CARE
            confidence = 0.6
            facts.append(f"Stated patient preference: '{case.patient_factors.patient_preferences}'.")
            citations.append("kb-patient-preference")
        elif case.patient_factors.performance_status:
            recommendation = RecommendationCategory.CONTINUE_CURRENT_THERAPY
            confidence = 0.6
            facts.append(f"Performance status reported as: '{case.patient_factors.performance_status}', no major functional concerns noted.")
        else:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.3
            facts.append("No performance status or patient preference information available.")

        rationale = self._compose_rationale(
            case, recommendation, facts, [self._kb.get(c) for c in citations]
        )
        return AgentOpinion(
            agent_name=self.name,
            round_number=1,
            recommendation=recommendation,
            confidence=confidence,
            rationale=rationale,
            cited_evidence=citations,
            facts_considered=facts,
        )
